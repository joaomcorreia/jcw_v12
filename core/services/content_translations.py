import hashlib
import json

from core.content_blocks import (
    BRAND_GLOSSARY_TERMS,
    PILOT_CONTENT_BLOCK_DEFINITIONS,
    build_default_block_payload,
    get_content_block_ui_label,
    get_supported_content_languages,
)
from core.models import ContentBlock, ContentBlockTranslation, ContentGlossaryTerm, ContentSiteSettings, Site
from core.services.ai_translation import get_content_translation_backend


def build_revision_hash(payload):
    serialized = json.dumps(payload or {}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def ensure_content_site_settings(site):
    settings_obj, _created = ContentSiteSettings.objects.get_or_create(site=site, defaults={"auto_translate_updates": True})
    return settings_obj


def ensure_glossary_terms():
    for term in BRAND_GLOSSARY_TERMS:
        ContentGlossaryTerm.objects.get_or_create(term=term, defaults={"preferred_translations": {}, "never_translate": True, "is_active": True})


def normalize_block_payload(block_key, payload, language_code="en"):
    defaults = build_default_block_payload(block_key, language_code)
    payload = payload or {}
    items = payload.get("items") if isinstance(payload, dict) else None
    normalized_items = []
    for index, default_item in enumerate(defaults.get("items", [])):
        current_item = items[index] if isinstance(items, list) and len(items) > index and isinstance(items[index], dict) else {}
        normalized_items.append({
            "title": str(current_item.get("title", default_item.get("title", ""))).strip(),
            "body": str(current_item.get("body", default_item.get("body", ""))).strip(),
        })
    return {
        "eyebrow": str(payload.get("eyebrow", defaults.get("eyebrow", ""))).strip(),
        "heading": str(payload.get("heading", defaults.get("heading", ""))).strip(),
        "intro": str(payload.get("intro", defaults.get("intro", ""))).strip(),
        "items": normalized_items,
    }


PAYLOAD_FIELDS = (
    "eyebrow", "heading", "intro",
    "item_1_title", "item_1_body",
    "item_2_title", "item_2_body",
    "item_3_title", "item_3_body",
)


def _payload_field_values(payload):
    payload = payload or {}
    items = payload.get("items", []) if isinstance(payload, dict) else []
    values = {"eyebrow": payload.get("eyebrow", ""), "heading": payload.get("heading", ""), "intro": payload.get("intro", "")}
    for index in range(3):
        item = items[index] if isinstance(items, list) and len(items) > index and isinstance(items[index], dict) else {}
        values[f"item_{index + 1}_title"] = item.get("title", "")
        values[f"item_{index + 1}_body"] = item.get("body", "")
    return values


def _payload_fields(payload, fields):
    values = _payload_field_values(payload)
    return {field: values[field] for field in fields}


def _merge_payload_fields(payload, translated_fields):
    merged = json.loads(json.dumps(payload or {}, ensure_ascii=False))
    values = _payload_field_values(merged)
    values.update(translated_fields)
    merged["eyebrow"] = values["eyebrow"]
    merged["heading"] = values["heading"]
    merged["intro"] = values["intro"]
    merged["items"] = [{"title": values[f"item_{index}_title"], "body": values[f"item_{index}_body"]} for index in range(1, 4)]
    return merged


def _changed_payload_fields(before, after):
    before_values = _payload_field_values(before)
    after_values = _payload_field_values(after)
    return [field for field in PAYLOAD_FIELDS if before_values[field] != after_values[field]]


def _translated_fields_from_response(data, requested_fields):
    if not isinstance(data, dict):
        raise ValueError("Translation response must be an object.")
    if "items" in data:
        values = _payload_field_values(data)
        return {field: values[field] for field in requested_fields if field in values}
    flat_fields = {field: data[field] for field in requested_fields if field in data}
    if flat_fields:
        return flat_fields
    return {}


def _can_partially_propagate_source_switch(block, language_code, old_source_hash):
    if language_code == (block.last_source_language or "en"):
        return True
    candidate = get_translation(block, language_code)
    if not candidate or candidate.is_protected or candidate.status != ContentBlockTranslation.STATUS_CURRENT:
        return False
    if candidate.source_revision_hash != old_source_hash or candidate.translated_from_revision_hash != old_source_hash:
        return False
    for other in block.translations.all():
        if other.language_code == language_code or other.is_protected:
            continue
        if other.status != ContentBlockTranslation.STATUS_CURRENT or other.source_revision_hash != old_source_hash or other.translated_from_revision_hash != old_source_hash or other.pending_fields:
            return False
    return True

def get_content_site_for_request(request=None):
    request_site = getattr(request, "site", None) if request else None
    if request_site and not request_site.is_main:
        return request_site
    return Site.objects.filter(is_main=True).first()


def ensure_pilot_content_blocks(site):
    if not site or not site.is_main:
        return []
    ensure_content_site_settings(site)
    ensure_glossary_terms()
    blocks = []
    for definition in PILOT_CONTENT_BLOCK_DEFINITIONS:
        block, _created = ContentBlock.objects.get_or_create(
            site=site,
            key=definition["key"],
            defaults={
                "slug": definition["slug"],
                "label": definition["label"],
                "placement": definition["placement"],
                "content_type": definition["content_type"],
                "is_active": True,
                "last_source_language": "en",
            },
        )
        english_payload = normalize_block_payload(definition["key"], build_default_block_payload(definition["key"], "en"), "en")
        english_hash = build_revision_hash(english_payload)
        if not block.last_source_language:
            block.last_source_language = "en"
            block.save(update_fields=["last_source_language"])
        for language_code in get_supported_content_languages():
            translation, created = ContentBlockTranslation.objects.get_or_create(
                block=block,
                language_code=language_code,
                defaults={
                    "payload_json": normalize_block_payload(definition["key"], build_default_block_payload(definition["key"], language_code), language_code),
                    "source_language": "en",
                    "source_revision_hash": english_hash,
                    "translated_from_revision_hash": english_hash,
                    "status": ContentBlockTranslation.STATUS_CURRENT,
                    "is_published": True,
                    "provenance": ContentBlockTranslation.PROVENANCE_SEEDED,
                },
            )
            if not created and not translation.payload_json:
                translation.payload_json = normalize_block_payload(definition["key"], build_default_block_payload(definition["key"], language_code), language_code)
                translation.source_language = translation.source_language or "en"
                translation.source_revision_hash = translation.source_revision_hash or english_hash
                translation.translated_from_revision_hash = translation.translated_from_revision_hash or english_hash
                translation.status = translation.status or ContentBlockTranslation.STATUS_CURRENT
                translation.provenance = translation.provenance or ContentBlockTranslation.PROVENANCE_SEEDED
                translation.save()
        blocks.append(block)
    return blocks


def get_translation(block, language_code, create=False):
    translation = block.translations.filter(language_code=language_code).first()
    if translation or not create:
        return translation
    return ContentBlockTranslation.objects.create(
        block=block,
        language_code=language_code,
        payload_json=normalize_block_payload(block.key, build_default_block_payload(block.key, language_code), language_code),
        source_language=block.last_source_language or "en",
        status=ContentBlockTranslation.STATUS_OUTDATED,
        provenance=ContentBlockTranslation.PROVENANCE_SEEDED,
        is_published=True,
        pending_fields=list(PAYLOAD_FIELDS),
    )


def get_block_payload(block, language_code):
    translation = get_translation(block, language_code)
    if translation and translation.is_published and isinstance(translation.payload_json, dict) and translation.payload_json:
        return normalize_block_payload(block.key, translation.payload_json, language_code)
    return normalize_block_payload(block.key, build_default_block_payload(block.key, language_code), language_code)


def get_content_block_payload(site, block_key, language_code):
    block = ContentBlock.objects.filter(site=site, key=block_key, is_active=True).prefetch_related("translations").first()
    if not block:
        return normalize_block_payload(block_key, build_default_block_payload(block_key, language_code), language_code)
    return get_block_payload(block, language_code)


def _glossary_for_language(language_code):
    glossary = []
    for term in ContentGlossaryTerm.objects.filter(is_active=True).order_by("term"):
        preferred = term.preferred_translations.get(language_code, "") if isinstance(term.preferred_translations, dict) else ""
        glossary.append({"term": term.term, "preferred_translation": preferred, "never_translate": term.never_translate})
    return glossary


def get_source_translation(block):
    language_code = block.last_source_language or "en"
    translation = block.translations.filter(language_code=language_code).first()
    return translation or block.translations.order_by("-updated_at").first()


def auto_update_block_translations(block, source_translation, backend=None, language_codes=None):
    backend = backend or get_content_translation_backend()
    target_codes = language_codes or get_supported_content_languages()
    if not backend.is_available():
        return {"updated_languages": [], "skipped_languages": [code for code in target_codes if code != source_translation.language_code], "failed_languages": [], "backend_available": False}
    updated_languages = []
    skipped_languages = []
    failed_languages = []
    for language_code in target_codes:
        if language_code == source_translation.language_code:
            continue
        existing_translation = block.translations.filter(language_code=language_code).first()
        translation = existing_translation or get_translation(block, language_code, create=True)
        if translation.is_protected or not translation.is_published:
            skipped_languages.append(language_code)
            continue
        requested_fields = list(translation.pending_fields or PAYLOAD_FIELDS)
        if not requested_fields and translation.translated_from_revision_hash == source_translation.source_revision_hash and translation.status == ContentBlockTranslation.STATUS_CURRENT:
            continue
        try:
            translated_payload = backend.translate_payload(
                block_label=block.label,
                site_name=block.site.name if block.site_id else "Just Code Works",
                source_language=source_translation.language_code,
                target_language=language_code,
                source_payload=source_translation.payload_json if set(requested_fields) == set(PAYLOAD_FIELDS) else _payload_fields(source_translation.payload_json, requested_fields),
                existing_target_payload=translation.payload_json if set(requested_fields) == set(PAYLOAD_FIELDS) else _payload_fields(translation.payload_json, requested_fields),
                glossary_terms=_glossary_for_language(language_code),
                fields=requested_fields,
            )
            translated_fields = _translated_fields_from_response(translated_payload, requested_fields)
            if not translated_fields:
                raise ValueError("Translation response contained no requested fields.")
        except Exception:
            translation.status = ContentBlockTranslation.STATUS_NEEDS_REVIEW
            translation.pending_fields = requested_fields
            translation.save(update_fields=["status", "pending_fields", "updated_at"])
            failed_languages.append(language_code)
            continue
        failed_fields = [field for field in requested_fields if field not in translated_fields]
        translation.payload_json = _merge_payload_fields(translation.payload_json, translated_fields)
        translation.source_language = source_translation.language_code
        translation.source_revision_hash = source_translation.source_revision_hash
        translation.translated_from_revision_hash = source_translation.source_revision_hash
        translation.pending_fields = failed_fields
        translation.status = ContentBlockTranslation.STATUS_NEEDS_REVIEW if failed_fields else ContentBlockTranslation.STATUS_CURRENT
        translation.provenance = ContentBlockTranslation.PROVENANCE_AUTOMATIC
        translation.save()
        if translated_fields:
            updated_languages.append(language_code)
        if failed_fields:
            failed_languages.append(language_code)
    return {"updated_languages": updated_languages, "skipped_languages": skipped_languages, "failed_languages": failed_languages, "backend_available": True}

def save_block_translation(block, language_code, payload, *, is_protected=False, is_published=True, auto_translate_enabled=True, backend=None):
    normalized_payload = normalize_block_payload(block.key, payload, language_code)
    existing_translation = get_translation(block, language_code)
    existing_payload = normalize_block_payload(block.key, existing_translation.payload_json, language_code) if existing_translation else None
    content_changed = existing_translation is None or existing_payload != normalized_payload
    translation = existing_translation or get_translation(block, language_code, create=True)

    if not content_changed:
        translation.is_protected = is_protected
        translation.is_published = is_published
        translation.save(update_fields=["is_protected", "is_published", "updated_at"])
        return {"translation": translation, "content_changed": False, "auto_result": {"updated_languages": [], "skipped_languages": [], "failed_languages": [], "backend_available": False}}

    old_source_language = block.last_source_language or "en"
    old_source_translation = get_translation(block, old_source_language)
    old_source_hash = old_source_translation.source_revision_hash if old_source_translation else ""
    partial_safe = _can_partially_propagate_source_switch(block, language_code, old_source_hash)
    changed_fields = _changed_payload_fields(existing_payload or {}, normalized_payload)
    source_revision_hash = build_revision_hash(normalized_payload)

    translation.payload_json = normalized_payload
    translation.pending_fields = []
    translation.source_language = language_code
    translation.source_revision_hash = source_revision_hash
    translation.translated_from_revision_hash = source_revision_hash
    translation.status = ContentBlockTranslation.STATUS_CURRENT
    translation.is_protected = is_protected
    translation.is_published = is_published
    translation.provenance = ContentBlockTranslation.PROVENANCE_MANUAL
    translation.save()

    block.last_source_language = language_code
    block.save(update_fields=["last_source_language", "updated_at"])

    for other_language in get_supported_content_languages():
        if other_language == language_code:
            continue
        other_translation = get_translation(block, other_language, create=True)
        if other_translation.is_protected:
            continue
        pending_fields = list(other_translation.pending_fields or [])
        if partial_safe:
            pending_fields = list(dict.fromkeys(pending_fields + changed_fields))
        else:
            pending_fields = list(PAYLOAD_FIELDS)
        other_translation.source_language = language_code
        other_translation.source_revision_hash = source_revision_hash
        other_translation.pending_fields = pending_fields
        other_translation.status = ContentBlockTranslation.STATUS_OUTDATED if pending_fields else ContentBlockTranslation.STATUS_CURRENT
        other_translation.save(update_fields=["source_language", "source_revision_hash", "pending_fields", "status", "updated_at"])

    auto_result = {"updated_languages": [], "skipped_languages": [], "failed_languages": [], "backend_available": False}
    if auto_translate_enabled:
        auto_result = auto_update_block_translations(block, translation, backend=backend)
    return {"translation": translation, "content_changed": True, "auto_result": auto_result}
def update_block_translations(block, backend=None):
    source_translation = get_source_translation(block)
    if not source_translation:
        return {"updated": [], "skipped": [], "failed": [], "backend_available": False}

    result = auto_update_block_translations(block, source_translation, backend=backend)
    return {
        "updated": [f"{block.key}:{code}" for code in result["updated_languages"]],
        "skipped": [f"{block.key}:{code}" for code in result["skipped_languages"]],
        "failed": [f"{block.key}:{code}" for code in result["failed_languages"]],
        "backend_available": result["backend_available"],
    }

def update_site_translations(site, backend=None):
    ensure_pilot_content_blocks(site)
    backend = backend or get_content_translation_backend()
    updated = []
    skipped = []
    failed = []
    for block in ContentBlock.objects.filter(site=site, is_active=True).prefetch_related("translations"):
        source_translation = get_source_translation(block)
        if not source_translation:
            continue
        result = auto_update_block_translations(block, source_translation, backend=backend)
        updated.extend([f"{block.key}:{code}" for code in result["updated_languages"]])
        skipped.extend([f"{block.key}:{code}" for code in result["skipped_languages"]])
        failed.extend([f"{block.key}:{code}" for code in result["failed_languages"]])
    return {"updated": updated, "skipped": skipped, "failed": failed, "backend_available": backend.is_available()}


def build_block_summary(block):
    by_language = {translation.language_code: translation for translation in block.translations.all()}
    languages = []
    for language_code in get_supported_content_languages():
        translation = by_language.get(language_code)
        languages.append({
            "code": language_code,
            "status": translation.status if translation else "missing",
            "is_protected": bool(translation and translation.is_protected),
            "updated_at": translation.updated_at if translation else None,
        })
    return {
        "block": block,
        "label": get_content_block_ui_label(block.key),
        "languages": languages,
        "last_source_language": block.last_source_language or "en",
        "has_pending": any(
            translation and not translation.is_protected and translation.status in (
                ContentBlockTranslation.STATUS_OUTDATED,
                ContentBlockTranslation.STATUS_NEEDS_REVIEW,
            )
            for translation in by_language.values()
        ),
    }

def get_block_summaries(site):
    ensure_pilot_content_blocks(site)
    blocks = ContentBlock.objects.filter(site=site, is_active=True).prefetch_related("translations")
    order = {definition["key"]: index for index, definition in enumerate(PILOT_CONTENT_BLOCK_DEFINITIONS)}
    blocks = sorted(blocks, key=lambda block: order.get(block.key, len(order)))
    return [build_block_summary(block) for block in blocks]

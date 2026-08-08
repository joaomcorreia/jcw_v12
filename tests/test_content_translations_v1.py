from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import ContentBlock, ContentBlockTranslation, Plan, Site
from core.services.content_translations import ensure_glossary_terms, ensure_pilot_content_blocks, get_block_payload, save_block_translation, update_site_translations

User = get_user_model()


class FakeTranslationBackend:
    def __init__(self):
        self.calls = []

    def is_available(self):
        return True

    def translate_payload(self, **kwargs):
        self.calls.append(kwargs)
        source = kwargs["source_payload"]
        return {
            "eyebrow": source["eyebrow"],
            "heading": f"[{kwargs['target_language'].upper()}] {source['heading']}",
            "intro": source["intro"],
            "items": source["items"],
        }


class FailingFrenchBackend(FakeTranslationBackend):
    def translate_payload(self, **kwargs):
        if kwargs["target_language"] == "fr":
            raise RuntimeError("simulated provider failure")
        return super().translate_payload(**kwargs)

class ContentTranslationsV1Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username="content-owner", password="testpass123")
        cls.plan = Plan.objects.create(key="content-plan", slug="content-plan")
        cls.main_site = Site.objects.create(owner=cls.owner, plan=cls.plan, name="Just Code Works", language="en", status=Site.STATUS_PUBLISHED, is_main=True)
        ensure_pilot_content_blocks(cls.main_site)
        ensure_glossary_terms()

    def test_existing_pilot_content_renders_for_all_languages(self):
        block = ContentBlock.objects.get(site=self.main_site, key="home-foundations")
        for code in ("en", "nl", "de", "fr", "es", "pt"):
            response = self.client.get(f"/{code}/", HTTP_HOST="justcodeworks.local")
            self.assertEqual(response.status_code, 200)
            payload = get_block_payload(block, code)
            self.assertContains(response, payload["heading"])

    def test_editing_english_marks_other_languages_outdated_and_auto_updates(self):
        backend = FakeTranslationBackend()
        block = ContentBlock.objects.get(site=self.main_site, key="home-foundations")
        payload = get_block_payload(block, "en")
        payload["heading"] = "Updated English source heading"
        result = save_block_translation(block, "en", payload, auto_translate_enabled=True, backend=backend)

        english = ContentBlockTranslation.objects.get(block=block, language_code="en")
        self.assertEqual(english.status, ContentBlockTranslation.STATUS_CURRENT)
        self.assertEqual(block.last_source_language, "en")
        self.assertTrue(result["auto_result"]["updated_languages"])

        dutch = ContentBlockTranslation.objects.get(block=block, language_code="nl")
        self.assertEqual(dutch.status, ContentBlockTranslation.STATUS_NEEDS_REVIEW)
        self.assertEqual(dutch.source_language, "en")
        self.assertEqual(dutch.source_revision_hash, english.source_revision_hash)

    def test_editing_dutch_afterward_switches_source_language(self):
        backend = FakeTranslationBackend()
        block = ContentBlock.objects.get(site=self.main_site, key="home-ai-business-tools")
        payload = get_block_payload(block, "nl")
        payload["heading"] = "Nederlandse bronkop"
        save_block_translation(block, "nl", payload, auto_translate_enabled=True, backend=backend)

        dutch = ContentBlockTranslation.objects.get(block=block, language_code="nl")
        french = ContentBlockTranslation.objects.get(block=block, language_code="fr")
        block.refresh_from_db()
        self.assertEqual(dutch.status, ContentBlockTranslation.STATUS_CURRENT)
        self.assertEqual(block.last_source_language, "nl")
        self.assertEqual(french.source_language, "nl")

    def test_protected_german_translation_is_not_overwritten(self):
        backend = FakeTranslationBackend()
        block = ContentBlock.objects.get(site=self.main_site, key="home-connected-systems")
        german = ContentBlockTranslation.objects.get(block=block, language_code="de")
        german.payload_json["heading"] = "Geschuetzte deutsche Fassung"
        german.is_protected = True
        german.save()

        payload = get_block_payload(block, "en")
        payload["heading"] = "Fresh source revision"
        save_block_translation(block, "en", payload, auto_translate_enabled=True, backend=backend)

        german.refresh_from_db()
        self.assertTrue(german.is_protected)
        self.assertEqual(german.payload_json["heading"], "Geschuetzte deutsche Fassung")
        self.assertEqual(german.display_status, "Protected")

    def _make_dutch_source(self, block):
        payload = get_block_payload(block, "nl")
        payload["heading"] = "Nieuwe Nederlandse bron"
        save_block_translation(block, "nl", payload, auto_translate_enabled=False)
        block.refresh_from_db()

    def test_editing_dutch_payload_makes_dutch_source(self):
        block = ContentBlock.objects.get(site=self.main_site, key="home-foundations")
        self._make_dutch_source(block)
        dutch = ContentBlockTranslation.objects.get(block=block, language_code="nl")
        self.assertEqual(block.last_source_language, "nl")
        self.assertEqual(dutch.status, ContentBlockTranslation.STATUS_CURRENT)
        self.assertEqual(dutch.source_language, "nl")

    def test_protecting_german_without_content_change_keeps_dutch_source(self):
        block = ContentBlock.objects.get(site=self.main_site, key="home-foundations")
        self._make_dutch_source(block)
        german = ContentBlockTranslation.objects.get(block=block, language_code="de")
        original_payload = german.payload_json.copy()
        save_block_translation(block, "de", original_payload, is_protected=True, auto_translate_enabled=False)
        block.refresh_from_db()
        german.refresh_from_db()
        self.assertEqual(block.last_source_language, "nl")
        self.assertTrue(german.is_protected)
        self.assertEqual(german.payload_json, original_payload)
        self.assertEqual(german.status, ContentBlockTranslation.STATUS_OUTDATED)

    def test_published_toggle_without_content_change_keeps_dutch_source(self):
        block = ContentBlock.objects.get(site=self.main_site, key="home-ai-business-tools")
        self._make_dutch_source(block)
        german = ContentBlockTranslation.objects.get(block=block, language_code="de")
        save_block_translation(block, "de", german.payload_json, is_published=False, auto_translate_enabled=False)
        block.refresh_from_db()
        german.refresh_from_db()
        self.assertEqual(block.last_source_language, "nl")
        self.assertFalse(german.is_published)

    def test_unchanged_german_submission_keeps_dutch_source(self):
        block = ContentBlock.objects.get(site=self.main_site, key="home-connected-systems")
        self._make_dutch_source(block)
        german = ContentBlockTranslation.objects.get(block=block, language_code="de")
        original_status = german.status
        save_block_translation(block, "de", german.payload_json, auto_translate_enabled=False)
        block.refresh_from_db()
        german.refresh_from_db()
        self.assertEqual(block.last_source_language, "nl")
        self.assertEqual(german.status, original_status)

    def test_actual_german_content_edit_makes_german_source(self):
        block = ContentBlock.objects.get(site=self.main_site, key="home-foundations")
        self._make_dutch_source(block)
        german = ContentBlockTranslation.objects.get(block=block, language_code="de")
        payload = german.payload_json.copy()
        payload["items"][0]["body"] = "Geaenderter deutscher Inhalt"
        save_block_translation(block, "de", payload, auto_translate_enabled=False)
        block.refresh_from_db()
        german.refresh_from_db()
        self.assertEqual(block.last_source_language, "de")
        self.assertEqual(german.status, ContentBlockTranslation.STATUS_CURRENT)
        self.assertEqual(german.payload_json["items"][0]["body"], "Geaenderter deutscher Inhalt")

    def test_protected_german_survives_later_dutch_source_edit(self):
        block = ContentBlock.objects.get(site=self.main_site, key="home-ai-business-tools")
        german = ContentBlockTranslation.objects.get(block=block, language_code="de")
        original_payload = german.payload_json.copy()
        save_block_translation(block, "de", original_payload, is_protected=True, auto_translate_enabled=False)
        self._make_dutch_source(block)
        block.refresh_from_db()
        german.refresh_from_db()
        self.assertEqual(block.last_source_language, "nl")
        self.assertTrue(german.is_protected)
        self.assertEqual(german.payload_json, original_payload)
        self.assertEqual(german.display_status, "Protected")
        french = ContentBlockTranslation.objects.get(block=block, language_code="fr")
        self.assertEqual(french.source_language, "nl")
        self.assertIn(french.status, (ContentBlockTranslation.STATUS_OUTDATED, ContentBlockTranslation.STATUS_NEEDS_REVIEW))
    def test_failed_target_does_not_rollback_source_or_other_targets(self):
        backend = FailingFrenchBackend()
        block = ContentBlock.objects.get(site=self.main_site, key="home-foundations")
        french = ContentBlockTranslation.objects.get(block=block, language_code="fr")
        original_french = french.payload_json.copy()
        payload = get_block_payload(block, "en")
        payload["heading"] = "Source survives provider failure"

        result = save_block_translation(block, "en", payload, auto_translate_enabled=True, backend=backend)

        english = ContentBlockTranslation.objects.get(block=block, language_code="en")
        french.refresh_from_db()
        german = ContentBlockTranslation.objects.get(block=block, language_code="de")
        self.assertEqual(english.status, ContentBlockTranslation.STATUS_CURRENT)
        self.assertIn("fr", result["auto_result"]["failed_languages"])
        self.assertEqual(french.payload_json, original_french)
        self.assertEqual(french.status, ContentBlockTranslation.STATUS_NEEDS_REVIEW)
        self.assertEqual(german.status, ContentBlockTranslation.STATUS_NEEDS_REVIEW)

    def test_pilot_blocks_are_main_site_only(self):
        tenant_owner = User.objects.create_user(username="scope-tenant-owner", password="testpass123")
        tenant = Site.objects.create(owner=tenant_owner, plan=self.plan, name="Scoped Tenant", subdomain="scope-tenant", language="en", status=Site.STATUS_PUBLISHED, is_main=False)
        self.assertEqual(ensure_pilot_content_blocks(tenant), [])
        self.assertFalse(ContentBlock.objects.filter(site=tenant).exists())
    def test_auto_update_off_keeps_translations_outdated_until_requested(self):
        backend = FakeTranslationBackend()
        block = ContentBlock.objects.get(site=self.main_site, key="home-foundations")
        self.main_site.content_settings.auto_translate_updates = False
        self.main_site.content_settings.save(update_fields=["auto_translate_updates"])

        payload = get_block_payload(block, "en")
        payload["heading"] = "Manual source without automatic updates"
        save_block_translation(block, "en", payload, auto_translate_enabled=False, backend=backend)

        spanish = ContentBlockTranslation.objects.get(block=block, language_code="es")
        self.assertEqual(spanish.status, ContentBlockTranslation.STATUS_OUTDATED)

        result = update_site_translations(self.main_site, backend=backend)
        spanish.refresh_from_db()
        self.assertTrue(result["updated"])
        self.assertEqual(spanish.status, ContentBlockTranslation.STATUS_NEEDS_REVIEW)

    def test_brand_glossary_terms_are_available_to_translation_backend(self):
        backend = FakeTranslationBackend()
        block = ContentBlock.objects.get(site=self.main_site, key="home-ai-business-tools")
        payload = get_block_payload(block, "en")
        payload["intro"] = "Just Code Works and PrintLab support multilingual publishing."
        save_block_translation(block, "en", payload, auto_translate_enabled=True, backend=backend)

        self.assertTrue(any(call["glossary_terms"] for call in backend.calls))
        terms = {entry["term"] for call in backend.calls for entry in call["glossary_terms"]}
        self.assertIn("Just Code Works", terms)
        self.assertIn("PrintLab", terms)

    def test_missing_db_content_falls_back_safely(self):
        block = ContentBlock.objects.get(site=self.main_site, key="home-foundations")
        ContentBlockTranslation.objects.filter(block=block, language_code="fr").delete()
        response = self.client.get("/fr/", HTTP_HOST="justcodeworks.local")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "syst")

    def test_site_isolation_for_content_blocks(self):
        tenant_owner = User.objects.create_user(username="tenant-owner", password="testpass123")
        tenant = Site.objects.create(owner=tenant_owner, plan=self.plan, name="Tenant Site", subdomain="tenant-one", language="en", status=Site.STATUS_PUBLISHED, is_main=False)
        self.assertEqual(ensure_pilot_content_blocks(tenant), [])
        self.assertFalse(ContentBlock.objects.filter(site=tenant).exists())
        self.assertTrue(ContentBlock.objects.filter(site=self.main_site, key="home-foundations").exists())

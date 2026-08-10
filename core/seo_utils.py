from urllib.parse import parse_qsl, urlsplit, urlencode

from django.conf import settings


INDEXABLE_PUBLIC_PATHS = frozenset({
    "/",
    "/about/",
    "/what-we-build/",
    "/how-we-work/",
    "/contact/",
    "/privacy-cookies/",
})


def is_indexable_public_path(path):
    """Return whether a path is one of the explicitly approved public pages."""
    stripped = _strip_lang_prefix(path, settings.LANGUAGES)
    normalized = _normalize_path("/" + stripped) if stripped else "/"
    return normalized in INDEXABLE_PUBLIC_PATHS


def is_indexable_public_request(request):
    """Only the main JCW site's approved marketing pages may be indexed."""
    site = getattr(request, "site", None)
    return bool(site and getattr(site, "is_main", False) and is_indexable_public_path(request.path))

def _normalize_path(path):
    if not path:
        return "/"
    if not path.startswith("/"):
        path = f"/{path}"
    if not path.endswith("/"):
        path = f"{path}/"
    return path


def _strip_lang_prefix(path, languages):
    path = _normalize_path(path)
    for code, _name in languages:
        prefix = f"/{code}/"
        if path.startswith(prefix):
            return path[len(prefix):]
        if path == f"/{code}":
            return ""
    return path.lstrip("/")


def _strip_tracking_params(full_path):
    parts = urlsplit(full_path)
    if not parts.query:
        return parts.path
    filtered = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not (key.startswith("utm_") or key in {"fbclid", "gclid"})
    ]
    if not filtered:
        return parts.path
    return f"{parts.path}?{urlencode(filtered, doseq=True)}"


def build_robots_meta(index=True, follow=True):
    if index is None:
        index = True
    if follow is None:
        follow = True
    return f"{'index' if index else 'noindex'}, {'follow' if follow else 'nofollow'}"


def build_language_url(request, lang_code):
    languages = settings.LANGUAGES
    remainder = _strip_lang_prefix(request.path, languages)
    if remainder:
        target_path = f"/{lang_code}/" + remainder
    else:
        target_path = f"/{lang_code}/"
    target_path = _normalize_path(target_path)
    return request.build_absolute_uri(target_path)


def build_language_path(lang_code, path):
    path = _normalize_path(path)
    if path == "/":
        return f"/{lang_code}/"
    return _normalize_path(f"/{lang_code}{path}")


def build_language_url_for_path(request, lang_code, path):
    return request.build_absolute_uri(build_language_path(lang_code, path))


def build_canonical_url(request):
    raw_path = _strip_tracking_params(request.get_full_path())
    path, sep, query = raw_path.partition("?")
    normalized_path = _normalize_path(path)
    if query:
        normalized_path = f"{normalized_path}?{query}"
    return request.build_absolute_uri(normalized_path)


def build_hreflang_urls(request):
    languages = settings.LANGUAGES
    alternates = []
    for code, _name in languages:
        alternates.append({"lang": code, "url": build_language_url(request, code)})
    default_lang = settings.LANGUAGE_CODE
    alternates.append({"lang": "x-default", "url": build_language_url(request, default_lang)})
    return alternates


def is_public_path(path):
    return is_indexable_public_path(path)


def resolve_canonical_override(request, override):
    if not override:
        return ""
    override = override.strip()
    if not override:
        return ""
    if override.startswith("http://") or override.startswith("https://"):
        return override
    if override.startswith("/"):
        return request.build_absolute_uri(override)
    return override


def resolve_page_seo(page, lang=None):
    if not page:
        return {"seo_title": "", "seo_description": "", "seo_robots": "index, follow", "canonical_override": ""}
    if lang and hasattr(page, "set_current_language"):
        page.set_current_language(lang)

    meta_title = None
    meta_description = None
    meta_index = None
    meta_follow = None
    canonical_override = ""
    if hasattr(page, "safe_translation_getter"):
        meta_title = page.safe_translation_getter("meta_title", any_language=True)
        meta_description = page.safe_translation_getter("meta_description", any_language=True)
        meta_index = page.safe_translation_getter("meta_robots_index", any_language=True)
        meta_follow = page.safe_translation_getter("meta_robots_follow", any_language=True)
        canonical_override = page.safe_translation_getter("canonical_override", any_language=True) or ""

    seo_title = meta_title or getattr(page, "seo_title", "") or getattr(page, "title", "") or getattr(page, "slug", "")
    seo_description = meta_description or getattr(page, "seo_description", "")
    seo_robots = build_robots_meta(meta_index, meta_follow)
    return {
        "seo_title": seo_title,
        "seo_description": seo_description,
        "seo_robots": seo_robots,
        "canonical_override": canonical_override,
    }

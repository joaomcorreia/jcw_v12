"""Shared language helpers for prefixed JCW routes."""

from urllib.parse import urlsplit, urlunsplit

from django.conf import settings

from core.seo_utils import build_language_path


def supported_language_codes():
    return {code for code, _name in settings.LANGUAGES}


def language_path_for_request(language, path):
    """Replace the current language prefix while preserving path and query."""
    parts = urlsplit(path or "/")
    current_path = parts.path or "/"
    for code, _name in settings.LANGUAGES:
        prefix = f"/{code}/"
        if current_path == f"/{code}" or current_path.startswith(prefix):
            current_path = current_path[len(prefix):] or "/"
            if not current_path.startswith("/"):
                current_path = f"/{current_path}"
            break
    target_path = build_language_path(language, current_path)
    return urlunsplit(("", "", target_path, parts.query, ""))


from django import template
from django.utils.translation import get_language

register = template.Library()


def _normalize_lang(language_code):
    code = (language_code or "").strip().lower().replace("_", "-")
    if not code:
        return ""
    return code.split("-", 1)[0]


@register.filter(name="t")
def translate_dict(value, fallback="en"):
    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return ""

    lang = _normalize_lang(get_language()) or "en"
    fallback_lang = _normalize_lang(fallback) or "en"

    if lang in value:
        return value.get(lang) or ""
    for key, translated_value in value.items():
        if _normalize_lang(key) == lang:
            return translated_value or ""

    if fallback_lang in value:
        return value.get(fallback_lang) or ""
    for key, translated_value in value.items():
        if _normalize_lang(key) == fallback_lang:
            return translated_value or ""

    for translated_value in value.values():
        if translated_value not in (None, ""):
            return translated_value
    return ""

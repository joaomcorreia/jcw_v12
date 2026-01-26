from django import template
from django.utils.translation import get_language

from core.models import Page, PageSection

register = template.Library()


@register.simple_tag
def site_field(site, page_slug, section_key, field_key, lang=None, default=""):
    if not site:
        return default
    page = Page.objects.filter(site=site, slug=page_slug).first()
    if not page:
        return default
    section = (
        PageSection.objects.filter(page=page, key=section_key)
        .select_related("content")
        .first()
    )
    if not section or not hasattr(section, "content"):
        return default
    content = section.content
    language = lang or get_language()
    if hasattr(content, "set_current_language"):
        content.set_current_language(language)
    if hasattr(content, "safe_translation_getter"):
        value = content.safe_translation_getter(field_key, default=default, language_code=language)
        return value or default
    value = getattr(content, field_key, None)
    if value is None:
        return default
    return value or default

from django import template
from django.utils.translation import get_language

from core.services.content_translations import get_content_block_payload, get_content_site_for_request

register = template.Library()


@register.filter
def dict_get(mapping, key):
    if not isinstance(mapping, dict):
        return ""
    return mapping.get(key, "")


@register.simple_tag(takes_context=True)
def get_content_block(context, block_key):
    request = context.get("request")
    language_code = (get_language() or "en").split("-", 1)[0]
    site = get_content_site_for_request(request)
    return get_content_block_payload(site, block_key, language_code)

from django.core.cache import cache
from core.models import SiteSettings


SETTINGS_CACHE_KEY = "jcw_site_settings"


def get_site_settings():
    settings = cache.get(SETTINGS_CACHE_KEY)
    if settings is None:
        settings = SiteSettings.objects.first()
        if settings is None:
            settings = SiteSettings.objects.create()
        cache.set(SETTINGS_CACHE_KEY, settings, 30)
    return settings

from django.contrib import admin

from .models import ManagedSite


@admin.register(ManagedSite)
class ManagedSiteAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "is_active", "default_language")
    list_filter = ("is_active", "default_language")
    search_fields = ("name", "domain")

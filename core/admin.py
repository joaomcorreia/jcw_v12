from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline

from .models import (
    Feature,
    BlogCategory,
    BlogPost,
    City,
    HeroParticlesSettings,
    MediaAsset,
    Page,
    PageSection,
    Plan,
    PlanFeature,
    PlanSEOSettings,
    RightSidebarPanel,
    Subscription,
    SectionContent,
    Site,
    SiteSettings,
    SiteVisibility,
    TenantSEOSettings,
    WebsiteTemplate,
)
from core.visibility_rules import sync_visibility_from_plan


def get_model_field_names(model):
    field_names = set()
    for field in model._meta.get_fields():
        if not getattr(field, "concrete", False):
            continue
        if getattr(field, "many_to_many", False):
            continue
        field_names.add(field.name)
    return field_names


def pick_fields(model, preferred_list, fallback_list=None, max_n=None):
    field_names = get_model_field_names(model)
    picked = []
    for name in preferred_list:
        if name in field_names and name not in picked:
            picked.append(name)
    if fallback_list:
        for name in fallback_list:
            if name in field_names and name not in picked:
                picked.append(name)
    if max_n:
        return picked[:max_n]
    return picked


def _get_field(model, field_name):
    try:
        return model._meta.get_field(field_name)
    except Exception:
        return None


def pick_search_fields(model, candidates):
    picked = []
    for candidate in candidates:
        if "__" in candidate:
            root, subfield = candidate.split("__", 1)
            root_field = _get_field(model, root)
            if not root_field or not root_field.is_relation:
                continue
            related_model = getattr(root_field, "related_model", None)
            if not related_model:
                continue
            if not _get_field(related_model, subfield):
                continue
            picked.append(candidate)
        else:
            if _get_field(model, candidate):
                picked.append(candidate)
    return picked


class PageSectionInline(admin.TabularInline):
    model = PageSection
    extra = 0
    fields = ("key", "order", "is_visible")
    ordering = ("order",)


@admin.register(Page)
class PageAdmin(TranslatableAdmin):
    list_display = ("slug", "is_active", "template_key")
    list_filter = ("is_active",)
    search_fields = ("slug", "translations__title")
    inlines = [PageSectionInline]


class SectionContentInline(TranslatableTabularInline):
    model = SectionContent
    extra = 0


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ("page", "key", "order", "is_visible")
    list_filter = ("page", "is_visible")
    ordering = ("page", "order", "id")
    inlines = [SectionContentInline]


@admin.register(SectionContent)
class SectionContentAdmin(TranslatableAdmin):
    list_display = ("section",)
    search_fields = ("section__key", "translations__heading")


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "is_enabled", "is_paid")
    list_filter = ("is_enabled", "is_paid")
    search_fields = ("key", "name")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("key",)
        return ()


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("slug", "name")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title_preview", "category", "is_published", "published_at")
    list_filter = ("is_published", "category")
    search_fields = ("slug", "title")
    ordering = ("-published_at", "-created_at")

    def title_preview(self, obj):
        return obj.get_title("en") or obj.slug

    title_preview.short_description = "Title"


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 0


@admin.register(Plan)
class PlanAdmin(TranslatableAdmin):
    list_display = ("key", "is_active", "sort_order")
    list_filter = ("is_active",)
    ordering = ("sort_order", "key")
    inlines = [PlanFeatureInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("key",)
        return ()


@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ("plan", "feature", "is_enabled")
    list_filter = ("plan", "feature", "is_enabled")


@admin.register(PlanSEOSettings)
class PlanSEOSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "plan",
        "seo_tier",
        "max_cities",
        "schema_level",
        "sitemap_url_cap",
        "allow_country_visibility",
        "allow_eu_visibility",
        "allow_hreflang",
        "allow_indexing",
    )
    list_filter = ("seo_tier", "schema_level", "allow_hreflang", "allow_indexing")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("plan", "status", "site", "started_at", "ends_at")
    list_filter = ("status", "plan")
    search_fields = ("plan__translations__name", "site__name")


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = pick_fields(
        Site,
        ["name", "owner", "status", "language", "template_key", "created_at"],
        ["id", "slug", "updated_at", "created", "modified"],
        max_n=6,
    )
    list_filter = pick_fields(
        Site,
        ["status", "language"],
        ["created_at", "updated_at", "created", "modified"],
    )
    search_fields = pick_search_fields(Site, ["name", "owner__username"])

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        sync_visibility_from_plan(obj)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = pick_fields(
        SiteSettings,
        ["launch_noindex", "launch_disallow_robots", "updated_at"],
        ["id"],
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(SiteVisibility)
class SiteVisibilityAdmin(admin.ModelAdmin):
    list_display = pick_fields(
        SiteVisibility,
        ["site", "visibility_mode", "seo_level", "last_updated"],
        ["id", "is_manual_override"],
    )
    list_filter = pick_fields(
        SiteVisibility,
        ["visibility_mode", "seo_level"],
        ["is_manual_override"],
    )
    search_fields = pick_search_fields(
        SiteVisibility, ["site__name", "site__owner__username"]
    )
    list_editable = (
        ["visibility_mode"] if "visibility_mode" in list_display else []
    )


@admin.register(WebsiteTemplate)
class WebsiteTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("name", "slug")


@admin.register(HeroParticlesSettings)
class HeroParticlesSettingsAdmin(admin.ModelAdmin):
    list_display = ("feature", "apply_to", "is_enabled")
    list_filter = ("is_enabled",)
    readonly_fields = ("apply_to_hint",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "feature",
                    "apply_to",
                    "is_enabled",
                    "config_json",
                    "apply_to_hint",
                )
            },
        ),
    )

    def apply_to_hint(self, obj=None):
        return "Toggle in Admin -> CORE -> Hero particles settings."

    apply_to_hint.short_description = "Preview"


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "created_at")
    search_fields = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "country_code", "is_top_city")
    list_filter = ("country_code", "is_top_city")
    search_fields = ("name", "slug", "country_code")


@admin.register(TenantSEOSettings)
class TenantSEOSettingsAdmin(admin.ModelAdmin):
    list_display = ("tenant", "target_country_code", "active_city", "last_city_change_at")
    list_filter = ("target_country_code",)
    search_fields = ("tenant__name", "tenant__owner__username", "active_city__name")


@admin.register(RightSidebarPanel)
class RightSidebarPanelAdmin(TranslatableAdmin):
    list_display = ("headline_preview", "page", "is_enabled", "show_social")
    list_filter = ("is_enabled", "show_social")
    search_fields = ("translations__headline", "email", "phone")

    def headline_preview(self, obj):
        return obj.safe_translation_getter("headline", any_language=True)

    headline_preview.short_description = "Headline"

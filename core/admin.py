from django.contrib import admin
from parler.admin import TranslatableAdmin, TranslatableTabularInline

from .models import (
    Feature,
    BlogCategory,
    BlogPost,
    HeroParticlesSettings,
    MediaAsset,
    Page,
    PageSection,
    Plan,
    PlanFeature,
    RightSidebarPanel,
    Subscription,
    SectionContent,
    Site,
    SiteSettings,
    WebsiteTemplate,
)


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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("plan", "status", "site", "started_at", "ends_at")
    list_filter = ("status", "plan")
    search_fields = ("plan__translations__name", "site__name")


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "language", "template_key", "created_at")
    list_filter = ("status", "language")
    search_fields = ("name", "owner__username")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("launch_noindex", "launch_disallow_robots", "updated_at")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(WebsiteTemplate)
class WebsiteTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("name", "slug")


@admin.register(HeroParticlesSettings)
class HeroParticlesSettingsAdmin(admin.ModelAdmin):
    list_display = ("feature", "apply_to")
    readonly_fields = ("apply_to_hint",)
    fieldsets = (
        (None, {"fields": ("feature", "apply_to", "config_json", "apply_to_hint")}),
    )

    def apply_to_hint(self, obj=None):
        return "Applies to homepage hero"

    apply_to_hint.short_description = "Preview"


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("name", "file", "created_at")
    search_fields = ("name",)


@admin.register(RightSidebarPanel)
class RightSidebarPanelAdmin(TranslatableAdmin):
    list_display = ("headline_preview", "page", "is_enabled", "show_social")
    list_filter = ("is_enabled", "show_social")
    search_fields = ("translations__headline", "email", "phone")

    def headline_preview(self, obj):
        return obj.safe_translation_getter("headline", any_language=True)

    headline_preview.short_description = "Headline"

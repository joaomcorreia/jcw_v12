from django.db import models
from django.db.models import Q
from parler.models import TranslatableModel, TranslatedFields


def get_localized_text(value_map, language_code, fallback="en"):
    if not value_map:
        return ""
    if isinstance(value_map, str):
        return value_map
    if not isinstance(value_map, dict):
        return str(value_map)
    return (
        value_map.get(language_code)
        or value_map.get(fallback)
        or next(iter(value_map.values()), "")
    )


class Page(TranslatableModel):
    slug = models.SlugField()
    is_active = models.BooleanField(default=True)
    template_key = models.CharField(max_length=100, blank=True)
    show_in_nav = models.BooleanField(default=True)
    nav_order = models.PositiveIntegerField(default=100)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    noindex = models.BooleanField(default=False)
    site = models.ForeignKey(
        "Site",
        on_delete=models.CASCADE,
        related_name="pages",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    translations = TranslatedFields(
        title=models.CharField(max_length=200),
        nav_label=models.CharField(max_length=120, blank=True),
        menu_subtitle=models.CharField(max_length=200, blank=True),
        meta_title=models.CharField(max_length=200),
        meta_description=models.TextField(blank=True),
        meta_robots_index=models.BooleanField(default=True),
        meta_robots_follow=models.BooleanField(default=True),
        canonical_override=models.CharField(max_length=300, blank=True),
    )

    class Meta:
        ordering = ["slug"]
        constraints = [
            models.UniqueConstraint(
                fields=["site", "slug"],
                name="uniq_page_slug_per_site",
            )
        ]

    def __str__(self):
        return self.slug


class PageSection(models.Model):
    page = models.ForeignKey(Page, related_name="sections", on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("page", "key")

    def __str__(self):
        return f"{self.page.slug}:{self.key}"


class SectionContent(TranslatableModel):
    section = models.OneToOneField(
        PageSection, related_name="content", on_delete=models.CASCADE
    )
    config_json = models.JSONField(default=dict, blank=True)
    # Per-language section payloads, e.g. {"en": {...}, "nl": {...}, "pt": {...}}.
    # Templates should use the i18n payload first and fall back to config_json.
    config_json_i18n = models.JSONField(
        default=dict,
        blank=True,
        help_text='Per-language content map, e.g. {"en": {...}, "nl": {...}, "pt": {...}}',
    )

    translations = TranslatedFields(
        heading=models.CharField(max_length=200, blank=True),
        subheading=models.TextField(blank=True),
        body=models.TextField(blank=True),
        cta_primary_text=models.CharField(max_length=120, blank=True),
        cta_primary_url=models.CharField(max_length=200, blank=True),
        cta_secondary_text=models.CharField(max_length=120, blank=True),
        cta_secondary_url=models.CharField(max_length=200, blank=True),
    )

    def __str__(self):
        return f"{self.section.page.slug}:{self.section.key}"


class Feature(models.Model):
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(
        blank=True,
        help_text="Printful API integration and uploads will be added in a later phase.",
    )
    is_enabled = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.key


class Plan(TranslatableModel):
    key = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    is_frozen = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    stripe_product_id = models.CharField(
        max_length=120,
        blank=True,
        help_text="Paste Stripe IDs here when activating payments",
    )
    stripe_price_id = models.CharField(
        max_length=120,
        blank=True,
        help_text="Paste Stripe IDs here when activating payments",
    )
    billing_interval = models.CharField(max_length=20, default="month")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        description=models.TextField(blank=True),
        price_display=models.CharField(max_length=100, blank=True),
    )

    class Meta:
        ordering = ["sort_order", "key"]

    def __str__(self):
        return self.key

    @property
    def display_name(self):
        name = ""
        if hasattr(self, "safe_translation_getter"):
            name = self.safe_translation_getter("name", any_language=True) or ""
        return name or self.key


class PlanSEOSettings(models.Model):
    SCHEMA_NONE = "none"
    SCHEMA_BASIC = "basic"
    SCHEMA_FULL = "full"
    SCHEMA_LEVEL_CHOICES = [
        (SCHEMA_NONE, "None"),
        (SCHEMA_BASIC, "Basic"),
        (SCHEMA_FULL, "Full"),
    ]

    META_BASIC = "basic"
    META_FULL = "full"
    META_LEVEL_CHOICES = [
        (META_BASIC, "Basic"),
        (META_FULL, "Full"),
    ]

    SEO_TIER_CHOICES = [
        ("local", "Local"),
        ("country", "Country"),
        ("eu", "EU"),
    ]

    plan = models.OneToOneField(
        Plan,
        on_delete=models.CASCADE,
        related_name="seo_settings",
    )
    seo_tier = models.CharField(max_length=20, choices=SEO_TIER_CHOICES, default="local")
    max_cities = models.PositiveIntegerField(default=1)
    schema_level = models.CharField(
        max_length=20,
        choices=SCHEMA_LEVEL_CHOICES,
        default=SCHEMA_BASIC,
    )
    sitemap_url_cap = models.PositiveIntegerField(default=200)
    multilingual_meta_level = models.CharField(
        max_length=20,
        choices=META_LEVEL_CHOICES,
        default=META_BASIC,
    )
    allow_location_pages = models.BooleanField(default=True)
    allow_service_location_pages = models.BooleanField(default=False)
    allow_city_switching = models.BooleanField(default=True)
    allow_country_visibility = models.BooleanField(default=False)
    allow_eu_visibility = models.BooleanField(default=False)
    allow_custom_canonical = models.BooleanField(default=False)
    allow_hreflang = models.BooleanField(default=True)
    allow_indexing = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"seo:{self.plan.key}"


class PlanFeature(models.Model):
    plan = models.ForeignKey(Plan, related_name="plan_features", on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, related_name="feature_plans", on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ("plan", "feature")
        ordering = ["plan_id", "feature_id"]

    def __str__(self):
        return f"{self.plan.key}:{self.feature.key}"


def default_particles_config():
    return {
        "particles": {
            "number": {"value": 80, "density": {"enable": True, "value_area": 800}},
            "color": {"value": "#ffffff"},
            "shape": {
                "type": "circle",
                "stroke": {"width": 0, "color": "#000000"},
                "polygon": {"nb_sides": 5},
            },
            "opacity": {
                "value": 0.5,
                "random": False,
                "anim": {
                    "enable": False,
                    "speed": 1,
                    "opacity_min": 0.1,
                    "sync": False,
                },
            },
            "size": {
                "value": 3,
                "random": True,
                "anim": {"enable": False, "speed": 40, "size_min": 0.1, "sync": False},
            },
            "line_linked": {
                "enable": True,
                "distance": 150,
                "color": "#ffffff",
                "opacity": 0.4,
                "width": 1,
            },
            "move": {
                "enable": True,
                "speed": 2,
                "direction": "none",
                "random": False,
                "straight": False,
                "out_mode": "out",
                "bounce": False,
                "attract": {"enable": False, "rotateX": 600, "rotateY": 1200},
            },
        },
        "interactivity": {
            "detect_on": "canvas",
            "events": {
                "onhover": {"enable": True, "mode": "repulse"},
                "onclick": {"enable": True, "mode": "push"},
                "resize": True,
            },
            "modes": {
                "grab": {"distance": 400, "line_linked": {"opacity": 1}},
                "bubble": {"distance": 400, "size": 40, "duration": 2, "opacity": 8, "speed": 3},
                "repulse": {"distance": 200, "duration": 0.4},
                "push": {"particles_nb": 4},
                "remove": {"particles_nb": 2},
            },
        },
        "retina_detect": True,
    }


class HeroParticlesSettings(models.Model):
    feature = models.OneToOneField(
        Feature,
        on_delete=models.CASCADE,
        related_name="particles_settings",
        limit_choices_to={"key": "particles_hero"},
    )
    apply_to = models.CharField(max_length=50, default="home")
    is_enabled = models.BooleanField(default=False)
    config_json = models.JSONField(
        default=default_particles_config,
        help_text="particlesJS configuration object",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Hero particles settings"

    def __str__(self):
        return f"particles:{self.apply_to}"


class MediaAsset(models.Model):
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to="uploads/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField()
    country_code = models.CharField(max_length=2)
    is_top_city = models.BooleanField(default=False)

    class Meta:
        ordering = ["country_code", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug", "country_code"],
                name="uniq_city_slug_country",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.country_code})"


class BlogCategory(models.Model):
    name = models.JSONField(default=dict, blank=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["slug"]
        verbose_name_plural = "Blog categories"

    def __str__(self):
        return self.slug

    def get_name(self, language_code):
        return get_localized_text(self.name, language_code)


class BlogPost(models.Model):
    title = models.JSONField(default=dict, blank=True)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        BlogCategory, related_name="posts", on_delete=models.PROTECT
    )
    excerpt = models.JSONField(default=dict, blank=True)
    body = models.JSONField(default=dict, blank=True)
    featured_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.slug

    def get_title(self, language_code):
        return get_localized_text(self.title, language_code)

    def get_excerpt(self, language_code):
        return get_localized_text(self.excerpt, language_code)

    def get_body(self, language_code):
        return get_localized_text(self.body, language_code)


class RightSidebarPanel(TranslatableModel):
    page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="right_sidebar_panels",
    )
    is_enabled = models.BooleanField(default=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=200, blank=True)
    maps_url = models.URLField(blank=True)
    cta_url = models.CharField(max_length=200, blank=True)
    show_social = models.BooleanField(default=True)

    translations = TranslatedFields(
        headline=models.CharField(max_length=200, blank=True),
        intro=models.TextField(blank=True),
        cta_text=models.CharField(max_length=120, blank=True),
        extra_html=models.TextField(blank=True),
    )

    class Meta:
        ordering = ["-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["page"],
                condition=Q(page__isnull=False),
                name="unique_right_sidebar_panel_per_page",
            )
        ]

    def __str__(self):
        label = self.safe_translation_getter("headline", any_language=True) or "Sidebar Panel"
        if self.page:
            return f"{label} ({self.page.slug})"
        return f"{label} (default)"


class Subscription(models.Model):
    STATUS_INACTIVE = "inactive"
    STATUS_ACTIVE = "active"
    STATUS_CANCELED = "canceled"
    STATUS_PAST_DUE = "past_due"

    STATUS_CHOICES = [
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_CANCELED, "Canceled"),
        (STATUS_PAST_DUE, "Past due"),
    ]

    site = models.ForeignKey(
        "controlpanel.ManagedSite",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_INACTIVE)
    started_at = models.DateTimeField()
    ends_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at", "-id"]

    def __str__(self):
        return f"{self.plan.key}:{self.status}"


class ProFormaInvoice(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELED, "Canceled"),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    description = models.TextField()
    amount_eur = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"invoice:{self.id}:{self.status}"


class Site(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
    ]

    owner = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="sites",
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name="sites",
    )
    name = models.CharField(max_length=200)
    subdomain = models.SlugField(
        max_length=63,
        blank=True,
        unique=True,
        null=True,
        help_text="Subdomain for tenant routing (e.g., 'mim' for mim.justcodeworks.local)",
    )
    language = models.CharField(max_length=20, default="nl")
    template_key = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["is_main"],
                condition=Q(is_main=True),
                name="unique_main_site",
            )
        ]

    def __str__(self):
        return self.name


class BusinessProfile(models.Model):
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="business_profile",
    )
    business_name = models.CharField(max_length=200)
    category = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    phone = models.CharField(max_length=50, blank=True)
    email_public = models.EmailField(blank=True)
    website_goal = models.CharField(max_length=240)
    brand_color = models.CharField(max_length=20, blank=True)
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return f"profile:{self.user_id}:{self.business_name}"


class SiteSettings(models.Model):
    launch_noindex = models.BooleanField(default=True)
    launch_disallow_robots = models.BooleanField(default=True)
    business_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    socials = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"


class TenantHeroSettings(models.Model):
    site = models.OneToOneField(
        Site, related_name="hero_settings", on_delete=models.CASCADE
    )
    config_json = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Tenant hero settings"

    def __str__(self):
        return f"{self.site.name} hero settings"


class MainSiteSectionSettings(models.Model):
    page_key = models.CharField(max_length=100)
    section_key = models.CharField(max_length=100)
    settings_json = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("page_key", "section_key")
        verbose_name_plural = "Main site section settings"

    def __str__(self):
        return f"{self.page_key}:{self.section_key}"


class MainSiteContent(models.Model):
    key = models.CharField(max_length=200, db_index=True)
    language = models.CharField(max_length=12, db_index=True)
    value = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("key", "language"),
                name="unique_main_site_content_key_lang",
            )
        ]
        verbose_name_plural = "Main site content"

    def __str__(self):
        return f"{self.key} [{self.language}]"


class ContentBlock(models.Model):
    site = models.ForeignKey(
        "Site",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="content_blocks",
    )
    key = models.SlugField(max_length=120)
    slug = models.SlugField(max_length=120)
    label = models.CharField(max_length=200)
    placement = models.CharField(max_length=200, blank=True)
    content_type = models.CharField(max_length=80, default="homepage_cards_v1")
    is_active = models.BooleanField(default=True)
    last_source_language = models.CharField(max_length=12, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["site_id", "key"]
        constraints = [
            models.UniqueConstraint(fields=["site", "key"], name="unique_content_block_site_key"),
            models.UniqueConstraint(fields=["site", "slug"], name="unique_content_block_site_slug"),
        ]

    def __str__(self):
        site_label = f"site:{self.site_id}" if self.site_id else "global"
        return f"{site_label}:{self.key}"


class ContentSiteSettings(models.Model):
    site = models.OneToOneField("Site", on_delete=models.CASCADE, related_name="content_settings")
    auto_translate_updates = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"content-settings:{self.site_id}"


class ContentGlossaryTerm(models.Model):
    term = models.CharField(max_length=200, unique=True)
    preferred_translations = models.JSONField(default=dict, blank=True)
    never_translate = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["term"]

    def __str__(self):
        return self.term


class ContentBlockTranslation(models.Model):
    STATUS_CURRENT = "current"
    STATUS_OUTDATED = "outdated"
    STATUS_NEEDS_REVIEW = "needs_review"

    STATUS_CHOICES = [
        (STATUS_CURRENT, "Current"),
        (STATUS_OUTDATED, "Outdated"),
        (STATUS_NEEDS_REVIEW, "Needs review"),
    ]

    PROVENANCE_SEEDED = "seeded"
    PROVENANCE_MANUAL = "manual"
    PROVENANCE_AUTOMATIC = "automatic"

    PROVENANCE_CHOICES = [
        (PROVENANCE_SEEDED, "Seeded"),
        (PROVENANCE_MANUAL, "Manual"),
        (PROVENANCE_AUTOMATIC, "Automatic"),
    ]

    block = models.ForeignKey(ContentBlock, on_delete=models.CASCADE, related_name="translations")
    language_code = models.CharField(max_length=12)
    payload_json = models.JSONField(default=dict, blank=True)
    source_language = models.CharField(max_length=12, blank=True)
    source_revision_hash = models.CharField(max_length=64, blank=True)
    translated_from_revision_hash = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CURRENT)
    is_protected = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    provenance = models.CharField(max_length=20, choices=PROVENANCE_CHOICES, default=PROVENANCE_MANUAL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["block_id", "language_code"]
        constraints = [
            models.UniqueConstraint(fields=["block", "language_code"], name="unique_content_block_translation_language")
        ]

    def __str__(self):
        return f"{self.block.key}:{self.language_code}"

    @property
    def display_status(self):
        if self.is_protected:
            return "Protected"
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


class SiteVisibility(models.Model):
    MODE_BASIC = "basic"
    MODE_LOCATIONS = "locations"
    MODE_EU = "eu"

    MODE_CHOICES = [
        (MODE_BASIC, "Basic"),
        (MODE_LOCATIONS, "Locations"),
        (MODE_EU, "EU"),
    ]

    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="visibility",
    )
    seo_level = models.CharField(max_length=20, blank=True)
    allowed_countries = models.JSONField(default=list, blank=True)
    allowed_cities = models.JSONField(default=list, blank=True)
    visibility_mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES,
        default=MODE_BASIC,
    )
    is_manual_override = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"visibility:{self.site_id}"

    def save(self, *args, **kwargs):
        if not getattr(self, "_from_sync", False):
            if self.pk:
                previous = SiteVisibility.objects.filter(pk=self.pk).first()
                if previous and previous.visibility_mode != self.visibility_mode:
                    self.is_manual_override = True
        return super().save(*args, **kwargs)


class TenantSEOSettings(models.Model):
    tenant = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="seo_settings",
    )
    target_country_code = models.CharField(max_length=2, blank=True)
    active_city = models.ForeignKey(
        City,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="active_tenants",
    )
    focus_cities = models.ManyToManyField(
        City,
        blank=True,
        related_name="focused_tenants",
    )
    last_city_change_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"seo-settings:{self.tenant_id}"


def default_template_languages():
    return ["nl", "en", "fr", "de", "es", "pt"]


def default_template_sections():
    return []


class WebsiteTemplate(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    is_published = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    languages = models.JSONField(default=default_template_languages)
    sections = models.JSONField(default=default_template_sections)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return self.name

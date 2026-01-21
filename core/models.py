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
    is_active = models.BooleanField(default=True)
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

    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        description=models.TextField(blank=True),
        price_display=models.CharField(max_length=100, blank=True),
    )

    class Meta:
        ordering = ["sort_order", "key"]

    def __str__(self):
        return self.key


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
    name = models.CharField(max_length=200)
    language = models.CharField(max_length=20, default="nl")
    template_key = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class SiteSettings(models.Model):
    launch_noindex = models.BooleanField(default=True)
    launch_disallow_robots = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"


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

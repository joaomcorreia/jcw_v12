from django.db import migrations, models
import django.db.models.deletion


def seed_plan_settings(apps, schema_editor):
    Plan = apps.get_model("core", "Plan")
    PlanSEOSettings = apps.get_model("core", "PlanSEOSettings")
    Site = apps.get_model("core", "Site")
    try:
        PlanTranslation = apps.get_model("core", "PlanTranslation")
    except LookupError:
        PlanTranslation = None

    def ensure_translation(plan, name):
        if not PlanTranslation:
            return
        if PlanTranslation.objects.filter(master_id=plan.id, language_code="en").exists():
            return
        PlanTranslation.objects.create(
            master_id=plan.id,
            language_code="en",
            name=name,
            description="",
            price_display="",
        )

    def defaults_for_tier(tier):
        if tier == "eu":
            return {
                "seo_tier": "eu",
                "max_cities": 9999,
                "schema_level": "full",
                "sitemap_url_cap": 5000,
                "multilingual_meta_level": "full",
                "allow_location_pages": True,
                "allow_service_location_pages": True,
                "allow_city_switching": True,
            }
        if tier == "country":
            return {
                "seo_tier": "country",
                "max_cities": 6,
                "schema_level": "basic",
                "sitemap_url_cap": 1000,
                "multilingual_meta_level": "full",
                "allow_location_pages": True,
                "allow_service_location_pages": False,
                "allow_city_switching": True,
            }
        return {
            "seo_tier": "local",
            "max_cities": 1,
            "schema_level": "basic",
            "sitemap_url_cap": 200,
            "multilingual_meta_level": "basic",
            "allow_location_pages": True,
            "allow_service_location_pages": False,
            "allow_city_switching": True,
        }

    def tier_for_key(key):
        if key in {"pro", "premium", "eu"}:
            return "eu"
        if key in {"growth", "country"}:
            return "country"
        return "local"

    starter = Plan.objects.filter(key="starter").first()
    if not starter:
        starter = Plan.objects.create(
            key="starter",
            slug="starter",
            is_active=True,
            sort_order=0,
            billing_interval="month",
        )
        ensure_translation(starter, "Starter")

    for plan in Plan.objects.all():
        if not plan.slug:
            plan.slug = plan.key
            plan.save(update_fields=["slug"])
        display_name = plan.key.title() if plan.key else "Plan"
        ensure_translation(plan, display_name)
        tier = tier_for_key(plan.key or "")
        PlanSEOSettings.objects.get_or_create(plan=plan, defaults=defaults_for_tier(tier))

    Site.objects.filter(plan__isnull=True).update(plan=starter)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_city_tenant_seo_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="plan",
            name="slug",
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="plan",
            name="is_frozen",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="plan",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="plan",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.CreateModel(
            name="PlanSEOSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("seo_tier", models.CharField(choices=[("local", "Local"), ("country", "Country"), ("eu", "EU")], default="local", max_length=20)),
                ("max_cities", models.PositiveIntegerField(default=1)),
                ("schema_level", models.CharField(choices=[("none", "None"), ("basic", "Basic"), ("full", "Full")], default="basic", max_length=20)),
                ("sitemap_url_cap", models.PositiveIntegerField(default=200)),
                ("multilingual_meta_level", models.CharField(choices=[("basic", "Basic"), ("full", "Full")], default="basic", max_length=20)),
                ("allow_location_pages", models.BooleanField(default=True)),
                ("allow_service_location_pages", models.BooleanField(default=False)),
                ("allow_city_switching", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("plan", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="seo_settings", to="core.plan")),
            ],
        ),
        migrations.RunPython(seed_plan_settings, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="plan",
            name="slug",
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name="plan",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="plan",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="site",
            name="plan",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="sites", to="core.plan"),
        ),
    ]

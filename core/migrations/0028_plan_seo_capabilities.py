from django.db import migrations, models


def set_plan_seo_flags(apps, schema_editor):
    PlanSEOSettings = apps.get_model("core", "PlanSEOSettings")
    for settings in PlanSEOSettings.objects.all():
        tier = getattr(settings, "seo_tier", "local")
        allow_country = tier in {"country", "eu"}
        allow_eu = tier == "eu"
        allow_custom = tier == "eu"
        settings.allow_country_visibility = allow_country
        settings.allow_eu_visibility = allow_eu
        settings.allow_custom_canonical = allow_custom
        if settings.allow_hreflang is None:
            settings.allow_hreflang = True
        if settings.allow_indexing is None:
            settings.allow_indexing = True
        settings.save(
            update_fields=[
                "allow_country_visibility",
                "allow_eu_visibility",
                "allow_custom_canonical",
                "allow_hreflang",
                "allow_indexing",
            ]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0027_hero_particles_settings_enabled"),
    ]

    operations = [
        migrations.AddField(
            model_name="planseosettings",
            name="allow_country_visibility",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="planseosettings",
            name="allow_eu_visibility",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="planseosettings",
            name="allow_custom_canonical",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="planseosettings",
            name="allow_hreflang",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="planseosettings",
            name="allow_indexing",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(set_plan_seo_flags, migrations.RunPython.noop),
    ]

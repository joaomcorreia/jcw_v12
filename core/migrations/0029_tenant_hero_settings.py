from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0028_plan_seo_capabilities"),
    ]

    operations = [
        migrations.CreateModel(
            name="TenantHeroSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("config_json", models.JSONField(blank=True, default=dict)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "site",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hero_settings",
                        to="core.site",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Tenant hero settings",
            },
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0029_tenant_hero_settings"),
    ]

    operations = [
        migrations.CreateModel(
            name="MainSiteSectionSettings",
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
                ("page_key", models.CharField(max_length=100)),
                ("section_key", models.CharField(max_length=100)),
                ("settings_json", models.JSONField(blank=True, default=dict)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Main site section settings",
                "unique_together": {("page_key", "section_key")},
            },
        ),
    ]

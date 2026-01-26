import django
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0018_page_seo_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteVisibility",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("seo_level", models.CharField(blank=True, max_length=20)),
                ("allowed_countries", models.JSONField(blank=True, default=list)),
                ("allowed_cities", models.JSONField(blank=True, default=list)),
                ("visibility_mode", models.CharField(choices=[("basic", "Basic"), ("locations", "Locations"), ("eu", "EU")], default="basic", max_length=20)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                ("site", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="visibility", to="core.site")),
            ],
        ),
    ]

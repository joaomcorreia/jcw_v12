from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0023_add_site_subdomain"),
    ]

    operations = [
        migrations.CreateModel(
            name="City",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField()),
                ("country_code", models.CharField(max_length=2)),
                ("is_top_city", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["country_code", "name"],
            },
        ),
        migrations.CreateModel(
            name="TenantSEOSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("target_country_code", models.CharField(blank=True, max_length=2)),
                ("last_city_change_at", models.DateTimeField(blank=True, null=True)),
                ("active_city", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="active_tenants", to="core.city")),
                ("tenant", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="seo_settings", to="core.site")),
                ("focus_cities", models.ManyToManyField(blank=True, related_name="focused_tenants", to="core.city")),
            ],
        ),
        migrations.AddConstraint(
            model_name="city",
            constraint=models.UniqueConstraint(fields=("slug", "country_code"), name="uniq_city_slug_country"),
        ),
    ]


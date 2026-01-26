from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0025_plan_seo_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="pagetranslation",
            name="canonical_override",
            field=models.CharField(blank=True, max_length=300),
        ),
    ]

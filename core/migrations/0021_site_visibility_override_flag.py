from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0020_site_settings_schema_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitevisibility",
            name="is_manual_override",
            field=models.BooleanField(default=False),
        ),
    ]

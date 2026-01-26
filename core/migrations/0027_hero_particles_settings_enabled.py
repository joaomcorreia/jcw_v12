from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0026_page_translation_canonical_override"),
    ]

    operations = [
        migrations.AddField(
            model_name="heroparticlessettings",
            name="is_enabled",
            field=models.BooleanField(default=False),
        ),
    ]

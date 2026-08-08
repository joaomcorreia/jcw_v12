from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0038_seed_content_blocks_v1"),
    ]

    operations = [
        migrations.AddField(
            model_name="contentblocktranslation",
            name="pending_fields",
            field=models.JSONField(blank=True, default=list),
        ),
    ]

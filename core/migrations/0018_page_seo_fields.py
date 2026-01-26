from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0017_page_nav_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="seo_title",
            field=models.CharField(blank=True, max_length=70),
        ),
        migrations.AddField(
            model_name="page",
            name="seo_description",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name="page",
            name="noindex",
            field=models.BooleanField(default=False),
        ),
    ]

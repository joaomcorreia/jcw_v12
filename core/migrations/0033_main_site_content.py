from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0032_alter_mainsitesectionsettings_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="MainSiteContent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(db_index=True, max_length=200)),
                ("language", models.CharField(db_index=True, max_length=12)),
                ("value", models.TextField(blank=True, default="")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Main site content",
            },
        ),
        migrations.AddConstraint(
            model_name="mainsitecontent",
            constraint=models.UniqueConstraint(fields=("key", "language"), name="unique_main_site_content_key_lang"),
        ),
    ]

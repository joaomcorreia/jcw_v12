from django.db import migrations, models


def default_template_languages():
    return ["nl", "en", "fr", "de", "es", "pt"]


def default_template_sections():
    return []


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_blogcategory_blogpost"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebsiteTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("slug", models.SlugField(unique=True)),
                ("is_published", models.BooleanField(default=False)),
                ("description", models.TextField(blank=True)),
                ("languages", models.JSONField(default=default_template_languages)),
                ("sections", models.JSONField(default=default_template_sections)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-updated_at", "-created_at"],
            },
        ),
    ]

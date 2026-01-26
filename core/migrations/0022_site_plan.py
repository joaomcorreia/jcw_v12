from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0021_site_visibility_override_flag"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="sites",
                to="core.plan",
            ),
        ),
    ]

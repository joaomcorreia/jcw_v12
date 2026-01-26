from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_site_is_main"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="show_in_nav",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="page",
            name="nav_order",
            field=models.PositiveIntegerField(default=100),
        ),
    ]

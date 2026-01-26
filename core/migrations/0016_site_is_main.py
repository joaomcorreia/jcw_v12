from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_drop_slug_unique_index"),
    ]

    operations = [
        migrations.AddField(
            model_name="site",
            name="is_main",
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name="site",
            constraint=models.UniqueConstraint(
                fields=("is_main",),
                condition=Q(is_main=True),
                name="unique_main_site",
            ),
        ),
    ]

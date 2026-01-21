from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_websitetemplate"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="site",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.CASCADE,
                related_name="pages",
                to="core.site",
            ),
        ),
        migrations.AlterField(
            model_name="page",
            name="slug",
            field=models.SlugField(),
        ),
        migrations.AddConstraint(
            model_name="page",
            constraint=models.UniqueConstraint(
                fields=("site", "slug"),
                name="uniq_page_slug_per_site",
            ),
        ),
    ]

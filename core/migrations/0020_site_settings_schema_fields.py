from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0019_site_visibility"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="business_name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="phone",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="address_line1",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="address_line2",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="postal_code",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="city",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="country",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="logo",
            field=models.ImageField(blank=True, null=True, upload_to="site/"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="socials",
            field=models.JSONField(blank=True, default=list),
        ),
    ]

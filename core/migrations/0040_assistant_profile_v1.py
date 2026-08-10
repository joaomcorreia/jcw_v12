from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0039_contentblocktranslation_pending_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssistantProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("display_name", models.CharField(default="JCW Assistant", max_length=200)),
                ("role", models.CharField(blank=True, max_length=240)),
                ("purpose", models.TextField(blank=True)),
                ("enabled", models.BooleanField(default=True)),
                ("default_conversation_language", models.CharField(default="nl", max_length=12)),
                ("frontend_enabled", models.BooleanField(default=False)),
                ("backend_enabled", models.BooleanField(default=True)),
                ("business_description", models.TextField(blank=True)),
                ("business_facts", models.JSONField(blank=True, default=dict)),
                ("business_rules", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("site", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="assistant_profile", to="core.site")),
            ],
        ),
        migrations.CreateModel(
            name="AssistantCapability",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=80)),
                ("frontend_enabled", models.BooleanField(default=False)),
                ("backend_enabled", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="capabilities", to="core.assistantprofile")),
            ],
            options={
                "ordering": ["profile_id", "key"],
                "constraints": [
                    models.UniqueConstraint(fields=("profile", "key"), name="unique_assistant_profile_capability"),
                ],
            },
        ),
        migrations.CreateModel(
            name="AssistantLanguageConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language_code", models.CharField(max_length=12)),
                ("enabled", models.BooleanField(default=True)),
                ("greeting", models.TextField(blank=True)),
                ("welcome_message", models.TextField(blank=True)),
                ("fallback_message", models.TextField(blank=True)),
                ("handoff_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("profile", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="language_configs", to="core.assistantprofile")),
            ],
            options={
                "ordering": ["profile_id", "language_code"],
                "constraints": [
                    models.UniqueConstraint(fields=("profile", "language_code"), name="unique_assistant_profile_language"),
                ],
            },
        ),
    ]

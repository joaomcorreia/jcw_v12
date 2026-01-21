from django.db import models


LANGUAGE_CHOICES = [
    ("nl", "Dutch (Netherlands)"),
    ("en", "English"),
    ("fr", "French"),
    ("de", "German"),
    ("es", "Spanish"),
    ("pt", "Portuguese"),
]


class ManagedSite(models.Model):
    name = models.CharField(max_length=200)
    domain = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    default_language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default="nl"
    )
    enabled_languages = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

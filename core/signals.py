from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Site
from core.visibility_rules import sync_visibility_from_plan


@receiver(post_save, sender=Site)
def sync_visibility_on_site_save(sender, instance, **kwargs):
    sync_visibility_from_plan(instance)

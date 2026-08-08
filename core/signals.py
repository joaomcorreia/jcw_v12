from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Site
from core.visibility_rules import sync_visibility_from_plan
from core.services.content_translations import ensure_pilot_content_blocks


@receiver(post_save, sender=Site)
def sync_visibility_on_site_save(sender, instance, **kwargs):
    sync_visibility_from_plan(instance)


@receiver(post_save, sender=Site)
def seed_pilot_content_blocks_on_main_site_save(sender, instance, **kwargs):
    if instance.is_main:
        ensure_pilot_content_blocks(instance)

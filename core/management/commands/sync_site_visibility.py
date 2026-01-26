from django.core.management.base import BaseCommand

from core.models import Site
from core.visibility_rules import sync_visibility_from_plan


class Command(BaseCommand):
    help = "Sync SiteVisibility from the active plan."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Override manual visibility settings.",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        count = 0
        for site in Site.objects.all():
            sync_visibility_from_plan(site, force=force)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Synchronized {count} sites."))

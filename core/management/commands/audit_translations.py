from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Page, SectionContent


class Command(BaseCommand):
    help = "Audit missing translations for pages and sections."

    def handle(self, *args, **options):
        language_codes = [code for code, _ in settings.LANGUAGES]

        self.stdout.write("Pages missing translations:")
        for page in Page.objects.all().order_by("slug"):
            available = set(page.get_available_languages())
            missing = [code for code in language_codes if code not in available]
            if missing:
                self.stdout.write(f"- {page.slug}: {', '.join(missing)}")

        self.stdout.write("\nSections missing translations:")
        for section in SectionContent.objects.select_related("section__page"):
            available = set(section.get_available_languages())
            missing = [code for code in language_codes if code not in available]
            if missing:
                slug = section.section.page.slug
                key = section.section.key
                self.stdout.write(f"- {slug}/{key}: {', '.join(missing)}")

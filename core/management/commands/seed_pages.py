from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Page, PageSection, Plan, SectionContent, Site


def _get_default_plan():
    plan = Plan.objects.filter(key="starter").first()
    if plan:
        return plan
    return Plan.objects.order_by("sort_order", "key").first()


def _get_default_language():
    if hasattr(settings, "LANGUAGE_CODE") and settings.LANGUAGE_CODE:
        return settings.LANGUAGE_CODE
    languages = getattr(settings, "LANGUAGES", [])
    return languages[0][0] if languages else "en"


class Command(BaseCommand):
    help = "Seed core pages and sections required for DB-driven templates."

    def handle(self, *args, **options):
        main_site = Site.objects.filter(is_main=True).first()
        if not main_site:
            user_model = get_user_model()
            owner = user_model.objects.order_by("id").first()
            plan = _get_default_plan()
            if not owner or not plan:
                self.stdout.write(self.style.ERROR("Cannot create main site (missing user or plan)."))
                return
            main_site = Site.objects.create(
                owner=owner,
                name="Main Site",
                language=_get_default_language(),
                template_key="",
                status=Site.STATUS_PUBLISHED,
                is_main=True,
                plan=plan,
            )
            self.stdout.write(self.style.SUCCESS("Created main site."))

        page, created = Page.objects.get_or_create(
            site=main_site,
            slug="home",
            defaults={"is_active": True, "template_key": main_site.template_key},
        )
        if created:
            for code, _label in getattr(settings, "LANGUAGES", [("en", "English")]):
                page.set_current_language(code)
                page.title = "Home"
                page.meta_title = "Home"
                page.meta_description = ""
                page.save()
            self.stdout.write(self.style.SUCCESS("Created home page."))

        section_defs = [
            ("home.hero", 0, {"title": "", "subtitle": "", "cta_text": "", "cta_url": ""}),
            ("home.features", 1, {"heading": "", "intro": "", "items": []}),
            ("home.pricing", 2, {"heading": "", "intro": "", "items": []}),
            ("home.printlab", 3, {"heading": "", "intro": "", "items": []}),
            ("home.faq", 4, {"heading": "", "items": []}),
            ("home.cta", 5, {"heading": "", "body": "", "cta_text": "", "cta_url": ""}),
        ]

        for key, order, defaults in section_defs:
            section, _created = PageSection.objects.get_or_create(
                page=page,
                key=key,
                defaults={"order": order, "is_visible": True},
            )
            SectionContent.objects.get_or_create(
                section=section,
                defaults={"config_json": defaults},
            )

        self.stdout.write(self.style.SUCCESS("Ensured homepage sections."))

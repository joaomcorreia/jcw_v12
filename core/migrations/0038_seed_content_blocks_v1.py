from django.db import migrations
from django.utils import translation
from django.utils.translation import gettext
import hashlib
import json


BRAND_GLOSSARY_TERMS = [
    "Just Code Works",
    "JCW",
    "SiteExpress",
    "Get Online Fast",
    "ListaAcross",
    "TravelAcross",
    "PrintLab",
]


def build_revision_hash(payload):
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def build_defaults():
    return [
        {
            "key": "home-foundations",
            "slug": "home-foundations",
            "label": "Homepage: Digital systems built for the next stage.",
            "placement": "core.home_hq#builds",
            "content_type": "homepage_cards_v1",
            "builder": lambda: {
                "eyebrow": gettext("Foundations"),
                "heading": gettext("Digital systems built for the next stage."),
                "intro": gettext("Reusable platforms that connect products, services, workflows and operations."),
                "items": [
                    {"title": gettext("Custom platforms"), "body": gettext("Systems designed around specific products, services and business workflows.")},
                    {"title": gettext("Built for multiple markets"), "body": gettext("Flexible foundations for different languages, locations and commercial models.")},
                    {"title": gettext("Ready to grow"), "body": gettext("Platforms that can evolve into licensed, white-label or reseller opportunities.")},
                ],
            },
        },
        {
            "key": "home-ai-business-tools",
            "slug": "home-ai-business-tools",
            "label": "Homepage: AI-powered business tools",
            "placement": "core.home_hq#ai-business-tools",
            "content_type": "homepage_cards_v1",
            "builder": lambda: {
                "eyebrow": gettext("AI-powered business tools"),
                "heading": gettext("AI-powered business tools"),
                "intro": gettext("We build practical AI tools around real business information, helping companies support customers, create content, work across languages and automate repetitive tasks."),
                "items": [
                    {"title": gettext("Multilingual AI Assistants"), "body": gettext("Customer-facing assistants connected to business knowledge, with multilingual replies, lead capture, contact handoff and dashboard-based management.")},
                    {"title": gettext("Content & Localisation"), "body": gettext("AI tools for website copy, product and service descriptions, social content, FAQs and multilingual publishing.")},
                    {"title": gettext("Automation & Insights"), "body": gettext("Use enquiries, customer activity and business data to generate summaries, qualify leads, recommend actions and simplify recurring workflows.")},
                ],
            },
        },
        {
            "key": "home-connected-systems",
            "slug": "home-connected-systems",
            "label": "Homepage: Built as connected systems.",
            "placement": "core.home_hq#connected-systems",
            "content_type": "homepage_cards_v1",
            "builder": lambda: {
                "eyebrow": gettext("Connected Systems"),
                "heading": gettext("Built as connected systems."),
                "intro": gettext("A strong core can support focused products now and new opportunities later."),
                "items": [
                    {"title": gettext("Shared foundations"), "body": gettext("Common identity, data, language and workflow foundations keep related products consistent.")},
                    {"title": gettext("Independent products"), "body": gettext("Each product can stay focused on its users, proposition and commercial model.")},
                    {"title": gettext("Expandable infrastructure"), "body": gettext("New operators, markets and services can be added without rebuilding the platform from scratch.")},
                ],
            },
        },
    ]


def seed_content_blocks(apps, schema_editor):
    Site = apps.get_model("core", "Site")
    ContentBlock = apps.get_model("core", "ContentBlock")
    ContentBlockTranslation = apps.get_model("core", "ContentBlockTranslation")
    ContentGlossaryTerm = apps.get_model("core", "ContentGlossaryTerm")
    ContentSiteSettings = apps.get_model("core", "ContentSiteSettings")

    languages = ["en", "de", "es", "fr", "nl", "pt"]
    main_sites = Site.objects.filter(is_main=True)
    definitions = build_defaults()

    for site in main_sites:
        ContentSiteSettings.objects.get_or_create(site=site, defaults={"auto_translate_updates": True})
        for term in BRAND_GLOSSARY_TERMS:
            ContentGlossaryTerm.objects.get_or_create(term=term, defaults={"preferred_translations": {}, "never_translate": True, "is_active": True})
        for definition in definitions:
            block, _created = ContentBlock.objects.get_or_create(
                site=site,
                key=definition["key"],
                defaults={
                    "slug": definition["slug"],
                    "label": definition["label"],
                    "placement": definition["placement"],
                    "content_type": definition["content_type"],
                    "is_active": True,
                    "last_source_language": "en",
                },
            )
            with translation.override("en"):
                english_payload = definition["builder"]()
            english_hash = build_revision_hash(english_payload)
            for language_code in languages:
                with translation.override(language_code):
                    payload = definition["builder"]()
                ContentBlockTranslation.objects.get_or_create(
                    block=block,
                    language_code=language_code,
                    defaults={
                        "payload_json": payload,
                        "source_language": "en",
                        "source_revision_hash": english_hash,
                        "translated_from_revision_hash": english_hash,
                        "status": "current",
                        "is_protected": False,
                        "is_published": True,
                        "provenance": "seeded",
                    },
                )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0037_contentglossaryterm_contentblock_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_content_blocks, migrations.RunPython.noop),
    ]

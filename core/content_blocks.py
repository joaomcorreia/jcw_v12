from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy


PILOT_CONTENT_UI_LABELS = {
    "home-foundations": gettext_lazy("Homepage: Digital systems built for the next stage."),
    "home-ai-business-tools": gettext_lazy("Homepage: AI-powered business tools"),
    "home-connected-systems": gettext_lazy("Homepage: Built as connected systems."),
}


def get_content_block_ui_label(block_key):
    return PILOT_CONTENT_UI_LABELS.get(block_key, block_key)
BRAND_GLOSSARY_TERMS = [
    "Just Code Works",
    "JCW",
    "SiteExpress",
    "Get Online Fast",
    "ListaAcross",
    "TravelAcross",
    "PrintLab",
]


def get_supported_content_languages():
    return [code for code, _label in getattr(settings, "LANGUAGES", [("en", "English")])]


def _home_foundations_payload():
    return {
        "eyebrow": _("Foundations"),
        "heading": _("Digital systems built for the next stage."),
        "intro": _("Reusable platforms that connect products, services, workflows and operations."),
        "items": [
            {"title": _("Custom platforms"), "body": _("Systems designed around specific products, services and business workflows.")},
            {"title": _("Built for multiple markets"), "body": _("Flexible foundations for different languages, locations and commercial models.")},
            {"title": _("Ready to grow"), "body": _("Platforms that can evolve into licensed, white-label or reseller opportunities.")},
        ],
    }


def _home_ai_tools_payload():
    return {
        "eyebrow": _("AI-powered business tools"),
        "heading": _("AI-powered business tools"),
        "intro": _("We build practical AI tools around real business information, helping companies support customers, create content, work across languages and automate repetitive tasks."),
        "items": [
            {"title": _("Multilingual AI Assistants"), "body": _("Customer-facing assistants connected to business knowledge, with multilingual replies, lead capture, contact handoff and dashboard-based management.")},
            {"title": _("Content & Localisation"), "body": _("AI tools for website copy, product and service descriptions, social content, FAQs and multilingual publishing.")},
            {"title": _("Automation & Insights"), "body": _("Use enquiries, customer activity and business data to generate summaries, qualify leads, recommend actions and simplify recurring workflows.")},
        ],
    }


def _home_connected_systems_payload():
    return {
        "eyebrow": _("Connected Systems"),
        "heading": _("Built as connected systems."),
        "intro": _("A strong core can support focused products now and new opportunities later."),
        "items": [
            {"title": _("Shared foundations"), "body": _("Common identity, data, language and workflow foundations keep related products consistent.")},
            {"title": _("Independent products"), "body": _("Each product can stay focused on its users, proposition and commercial model.")},
            {"title": _("Expandable infrastructure"), "body": _("New operators, markets and services can be added without rebuilding the platform from scratch.")},
        ],
    }


PILOT_CONTENT_BLOCK_DEFINITIONS = [
    {"key": "home-foundations", "slug": "home-foundations", "label": "Homepage: Digital systems built for the next stage.", "placement": "core.home_hq#builds", "content_type": "homepage_cards_v1", "builder": _home_foundations_payload},
    {"key": "home-ai-business-tools", "slug": "home-ai-business-tools", "label": "Homepage: AI-powered business tools", "placement": "core.home_hq#ai-business-tools", "content_type": "homepage_cards_v1", "builder": _home_ai_tools_payload},
    {"key": "home-connected-systems", "slug": "home-connected-systems", "label": "Homepage: Built as connected systems.", "placement": "core.home_hq#connected-systems", "content_type": "homepage_cards_v1", "builder": _home_connected_systems_payload},
]


def get_pilot_content_block_definition(block_key):
    for definition in PILOT_CONTENT_BLOCK_DEFINITIONS:
        if definition["key"] == block_key:
            return definition
    raise KeyError(f"Unknown content block: {block_key}")


def build_default_block_payload(block_key, language_code=None):
    definition = get_pilot_content_block_definition(block_key)
    if language_code:
        with translation.override(language_code):
            return definition["builder"]()
    return definition["builder"]()

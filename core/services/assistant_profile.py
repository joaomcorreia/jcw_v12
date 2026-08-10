from copy import deepcopy

from django.conf import settings

from core.content_blocks import get_supported_content_languages
from core.models import AssistantCapability, AssistantLanguageConfig, AssistantProfile, BusinessProfile, ContentGlossaryTerm, Site

ASSISTANT_CAPABILITIES = {
    "answer_business_questions": {
        "label": "Answer business questions",
        "description": "Answer from approved business information.",
        "frontend": True,
        "backend": True,
    },
    "explain_services": {
        "label": "Explain services",
        "description": "Explain configured services and business offerings.",
        "frontend": True,
        "backend": True,
    },
    "explain_products": {
        "label": "Explain products",
        "description": "Explain configured products or product information.",
        "frontend": True,
        "backend": True,
    },
    "capture_lead": {
        "label": "Capture a lead",
        "description": "Collect an enquiry for human follow-up.",
        "frontend": True,
        "backend": False,
    },
    "handoff_to_human": {
        "label": "Handoff to a person",
        "description": "Offer configured human contact routes.",
        "frontend": True,
        "backend": True,
    },
    "inspect_website": {
        "label": "Inspect website",
        "description": "Read website structure for an operator.",
        "frontend": False,
        "backend": True,
    },
    "edit_content": {
        "label": "Edit content",
        "description": "Prepare controlled content changes for an operator.",
        "frontend": False,
        "backend": True,
    },
    "create_section": {
        "label": "Create a section",
        "description": "Prepare a section draft for approval.",
        "frontend": False,
        "backend": True,
    },
    "create_page": {
        "label": "Create a page",
        "description": "Prepare a page draft for approval.",
        "frontend": False,
        "backend": True,
    },
    "manage_translations": {
        "label": "Manage translations",
        "description": "Manage Content & Translations workflows.",
        "frontend": False,
        "backend": True,
    },
}

SUPPORTED_LANGUAGES = tuple(code for code, _label in settings.LANGUAGES)


def assistant_language_label(language_code):
    if language_code == "pt":
        return "Portuguese (pt-PT)"
    return dict(settings.LANGUAGES).get(language_code, language_code)


def _default_messages(language_code):
    messages = {
        "en": ("Hello. How can I help?", "I can help with approved business information.", "I do not have enough approved information to answer safely.", "Please contact the business team for confirmation."),
        "nl": ("Hallo. Hoe kan ik helpen?", "Ik kan helpen met goedgekeurde bedrijfsinformatie.", "Ik heb niet genoeg goedgekeurde informatie om veilig te antwoorden.", "Neem contact op met het bedrijf voor bevestiging."),
        "de": ("Hallo. Wie kann ich helfen?", "Ich kann mit freigegebenen Unternehmensinformationen helfen.", "Ich habe nicht genug freigegebene Informationen fuer eine sichere Antwort.", "Bitte kontaktieren Sie das Unternehmen zur Bestaetigung."),
        "es": ("Hola. Como puedo ayudar?", "Puedo ayudar con informacion empresarial aprobada.", "No tengo suficiente informacion aprobada para responder con seguridad.", "Contacte con el equipo para confirmacion."),
        "fr": ("Bonjour. Comment puis-je aider ?", "Je peux aider avec les informations approuvees de l'entreprise.", "Je n'ai pas assez d'informations approuvees pour repondre en securite.", "Contactez l'equipe pour confirmation."),
        "pt": ("Ola. Como posso ajudar?", "Posso ajudar com informacao empresarial aprovada.", "Nao tenho informacao aprovada suficiente para responder com seguranca.", "Contacte a equipa para confirmacao."),
    }
    greeting, welcome, fallback, handoff = messages.get(language_code, messages["en"])
    return {
        "greeting": greeting,
        "welcome_message": welcome,
        "fallback_message": fallback,
        "handoff_message": handoff,
    }


def ensure_assistant_profile(site):
    profile, _created = AssistantProfile.objects.get_or_create(
        site=site,
        defaults={
            "display_name": f"{site.name} Assistant",
            "role": "Business information assistant",
            "purpose": "Answer from approved business knowledge and guide users to the right next step.",
            "default_conversation_language": site.language if site.language in SUPPORTED_LANGUAGES else "nl",
            "frontend_enabled": False,
            "backend_enabled": True,
        },
    )
    for language_code in SUPPORTED_LANGUAGES:
        AssistantLanguageConfig.objects.get_or_create(
            profile=profile,
            language_code=language_code,
            defaults=_default_messages(language_code),
        )
    for key, definition in ASSISTANT_CAPABILITIES.items():
        AssistantCapability.objects.get_or_create(
            profile=profile,
            key=key,
            defaults={
                "frontend_enabled": definition["frontend"],
                "backend_enabled": definition["backend"],
            },
        )
    return profile


def assistant_site_for_request(request):
    tenant = getattr(request, "tenant", None)
    if tenant:
        return tenant
    site = getattr(request, "site", None)
    if site:
        return site
    return Site.objects.filter(is_main=True).first()


def user_can_access_assistant_site(user, site):
    return bool(site and user.is_authenticated and (user.is_staff or site.owner_id == user.id))


def enabled_language_configs(profile):
    return list(profile.language_configs.filter(enabled=True).order_by("language_code"))


def get_assistant_capabilities(profile, surface):
    if surface not in {"frontend", "backend"}:
        raise ValueError("Unsupported assistant surface.")
    if surface == "frontend" and not profile.frontend_enabled:
        return []
    if surface == "backend" and not profile.backend_enabled:
        return []
    enabled = []
    records = {record.key: record for record in profile.capabilities.all()}
    for key, definition in ASSISTANT_CAPABILITIES.items():
        record = records.get(key)
        enabled_for_surface = bool(record and getattr(record, f"{surface}_enabled"))
        if enabled_for_surface:
            enabled.append({
                "key": key,
                "label": definition["label"],
                "description": definition["description"],
            })
    return enabled


def capability_enabled(profile, capability_key, surface):
    return any(item["key"] == capability_key for item in get_assistant_capabilities(profile, surface))


def _business_knowledge(profile):
    site = profile.site
    business_profile = BusinessProfile.objects.filter(user_id=site.owner_id).first()
    facts = deepcopy(profile.business_facts or {})
    if business_profile:
        facts.setdefault("business_name", business_profile.business_name)
        facts.setdefault("category", business_profile.category)
        facts.setdefault("city", business_profile.city)
        facts.setdefault("country", business_profile.country)
        if business_profile.phone:
            facts.setdefault("phone", business_profile.phone)
        if business_profile.email_public:
            facts.setdefault("email", business_profile.email_public)
    facts = {key: value for key, value in facts.items() if value not in (None, "")}
    return {
        "description": profile.business_description,
        "facts": facts,
        "rules": deepcopy(profile.business_rules or {}),
        "unknown_fact_policy": "Do not invent facts. Use the configured fallback or human handoff message.",
    }


def build_assistant_context(profile, *, conversation_language, content_language=None, surface="backend"):
    config = profile.language_configs.filter(language_code=conversation_language, enabled=True).first()
    if not config:
        conversation_language = profile.default_conversation_language
        config = profile.language_configs.filter(language_code=conversation_language, enabled=True).first()
    if not config:
        config = profile.language_configs.filter(enabled=True).first()
        conversation_language = config.language_code if config else "en"
    if content_language and content_language not in SUPPORTED_LANGUAGES:
        content_language = None
    return {
        "assistant": {
            "name": profile.display_name,
            "role": profile.role,
            "purpose": profile.purpose,
            "enabled": profile.enabled,
        },
        "site": {
            "id": profile.site_id,
            "name": profile.site.name,
        },
        "business_knowledge": _business_knowledge(profile),
        "languages": {
            "conversation_language": conversation_language,
            "conversation_language_label": assistant_language_label(conversation_language),
            "content_language": content_language,
            "content_language_explicit": bool(content_language),
            "enabled": [item.language_code for item in enabled_language_configs(profile)],
        },
        "messages": {
            "greeting": config.greeting,
            "welcome": config.welcome_message,
            "fallback": config.fallback_message,
            "handoff": config.handoff_message,
        },
        "capabilities": get_assistant_capabilities(profile, surface),
        "surface": surface,
        "glossary": list(ContentGlossaryTerm.objects.filter(is_active=True).values("term", "preferred_translations", "never_translate")),
        "website_actions": {
            "enabled": capability_enabled(profile, "edit_content", "backend"),
            "execution_mode": "proposal-only",
        },
    }


def test_assistant_response(profile, *, message, conversation_language, content_language=None, surface="backend"):
    context = build_assistant_context(
        profile,
        conversation_language=conversation_language,
        content_language=content_language,
        surface=surface,
    )
    if not message.strip():
        return context["messages"]["greeting"], context
    if not context["business_knowledge"]["facts"] and not context["business_knowledge"]["description"]:
        return context["messages"]["fallback"], context
    return (
        "Test mode: the assistant would answer only from the configured business knowledge. "
        "Website actions are not executed in this foundation.",
        context,
    )

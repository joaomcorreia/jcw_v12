import json
import os

from core.content_blocks import get_content_block_ui_label, get_pilot_content_block_definition
from core.models import ContentBlock, ContentBlockTranslation
from core.services.assistant_profile import build_assistant_context
from core.services.content_translations import get_content_block_payload

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None


ASSISTANT_MODEL = "gpt-4.1-mini"
MAX_HISTORY_MESSAGES = 12


class AssistantServiceError(RuntimeError):
    """Safe, user-facing failure from the read-only assistant service."""


def assistant_model():
    return os.environ.get("JCW_ASSISTANT_MODEL", "").strip() or ASSISTANT_MODEL


def _content_context(profile, block_key, content_language):
    if not block_key or not content_language:
        return None
    try:
        definition = get_pilot_content_block_definition(block_key)
    except KeyError:
        return None
    block = ContentBlock.objects.filter(site=profile.site, key=block_key, is_active=True).first()
    if not block:
        return None
    translation = ContentBlockTranslation.objects.filter(block=block, language_code=content_language).first()
    return {
        "key": block.key,
        "label": str(get_content_block_ui_label(block.key)),
        "content_language": content_language,
        "content_type": definition["content_type"],
        "payload": get_content_block_payload(profile.site, block.key, content_language),
        "status": translation.status if translation else "not_configured",
    }


def build_authoritative_context(profile, *, conversation_language, content_language=None, surface="backend", content_block_key=None):
    context = build_assistant_context(
        profile,
        conversation_language=conversation_language,
        content_language=content_language,
        surface=surface,
    )
    context["authoritative_sources"] = {
        "site_identity": context["site"],
        "assistant_profile": context["assistant"],
        "business_knowledge": context["business_knowledge"],
        "language_messages": context["messages"],
        "glossary": context["glossary"],
        "capabilities": context["capabilities"],
    }
    content_context = _content_context(profile, content_block_key, context["languages"]["content_language"])
    if content_context:
        context["authoritative_sources"]["content_context"] = content_context
        context["content_context"] = content_context
    context["restricted_capabilities"] = [
        "edit_content",
        "create_section",
        "create_page",
        "manage_translations",
    ]
    context["execution_policy"] = {
        "read_only": True,
        "tools_exposed": False,
        "website_mutations": False,
        "unknown_fact_policy": "Do not invent facts; use the configured fallback or human handoff message.",
    }
    return context


def build_system_prompt(context):
    language = context["languages"]["conversation_language_label"]
    content_language = context["languages"].get("content_language") or "not selected"
    return (
        "You are the JCW Assistant for the site represented in the authoritative context below. "
        "Answer only from that context and the conversation. Never invent missing business facts. "
        f"Reply in {language}. The selected content language/context is {content_language}. "
        "Keep conversation language and content language independent. "
        "If information is missing, use the configured fallback or recommend human handoff. "
        "This is a read-only acceptance environment: do not edit content, create pages or sections, "
        "publish, change settings, or claim that an action was executed. "
        "The model may explain available capabilities, but JCW code is authoritative and no tools are exposed.\n\n"
        "AUTHORITATIVE CONTEXT (JSON):\n"
        + json.dumps(context["authoritative_sources"], ensure_ascii=False, sort_keys=True)
        + "\n\nEXECUTION POLICY (JSON):\n"
        + json.dumps(context["execution_policy"], ensure_ascii=False, sort_keys=True)
    )


def request_assistant_response(profile, *, message, conversation_language, content_language=None, surface="backend", content_block_key=None, history=None, client=None):
    if not message.strip():
        raise AssistantServiceError("Please enter a message for the assistant.")
    context = build_authoritative_context(
        profile,
        conversation_language=conversation_language,
        content_language=content_language,
        surface=surface,
        content_block_key=content_block_key,
    )
    api_key = os.environ.get("JCW_OPENAI_API_KEY", "").strip()
    if not api_key or OpenAI is None:
        raise AssistantServiceError("The assistant AI backend is not configured locally.")
    messages = [{"role": "system", "content": build_system_prompt(context)}]
    for item in (history or [])[-MAX_HISTORY_MESSAGES:]:
        if item.get("role") in {"user", "assistant"} and isinstance(item.get("content"), str):
            messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": message.strip()})
    try:
        api = client or OpenAI(api_key=api_key)
        response = api.responses.create(model=assistant_model(), input=messages)
    except Exception as exc:
        raise AssistantServiceError("The assistant could not complete that request. Please try again or use human handoff.") from exc
    text = (getattr(response, "output_text", "") or "").strip()
    if not text:
        raise AssistantServiceError("The assistant returned no answer. Please try again or use human handoff.")
    return text, context
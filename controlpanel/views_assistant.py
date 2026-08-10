from django import forms
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from core.content_blocks import PILOT_CONTENT_BLOCK_DEFINITIONS, get_content_block_ui_label
from core.services.assistant_engine import AssistantServiceError, request_assistant_response
from core.services.assistant_profile import (
    ASSISTANT_CAPABILITIES,
    SUPPORTED_LANGUAGES,
    assistant_language_label,
    assistant_site_for_request,
    build_assistant_context,
    ensure_assistant_profile,
    test_assistant_response,
    user_can_access_assistant_site,
)

ASSISTANT_SECTIONS = (
    ("overview", "Overview"),
    ("business", "Business Knowledge"),
    ("languages", "Languages & Messages"),
    ("capabilities", "Capabilities"),
    ("website_actions", "Website Actions"),
    ("test", "Test Assistant"),
)


class AssistantOverviewForm(forms.Form):
    display_name = forms.CharField(label=_("Assistant name"), max_length=200)
    role = forms.CharField(label=_("Role"), max_length=240, required=False)
    purpose = forms.CharField(label=_("Purpose"), widget=forms.Textarea(attrs={"rows": 4}), required=False)
    enabled = forms.BooleanField(label=_("Assistant enabled"), required=False)
    default_conversation_language = forms.ChoiceField(label=_("Default conversation language"))
    frontend_enabled = forms.BooleanField(label=_("Public assistant enabled"), required=False)
    backend_enabled = forms.BooleanField(label=_("Backend assistant enabled"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["default_conversation_language"].choices = [
            (code, assistant_language_label(code)) for code in SUPPORTED_LANGUAGES
        ]


class AssistantBusinessForm(forms.Form):
    business_description = forms.CharField(label=_("Business description"), widget=forms.Textarea(attrs={"rows": 6}), required=False)
    business_facts = forms.JSONField(
        label=_("Key business facts (JSON)"),
        widget=forms.Textarea(attrs={"rows": 8}),
        required=False,
    )
    business_rules = forms.JSONField(
        label=_("Business rules (JSON)"),
        widget=forms.Textarea(attrs={"rows": 8}),
        required=False,
    )


class AssistantTestForm(forms.Form):
    surface = forms.ChoiceField(label=_("Assistant surface"))
    conversation_language = forms.ChoiceField(label=_("Conversation language"))
    content_language = forms.ChoiceField(label=_("Content language"), required=False)
    content_block = forms.ChoiceField(label=_("Content context"), required=False)
    message = forms.CharField(label=_("Message"), widget=forms.Textarea(attrs={"rows": 4}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(code, assistant_language_label(code)) for code in SUPPORTED_LANGUAGES]
        self.fields["surface"].choices = [("frontend", _("Frontend")), ("backend", _("Backend"))]
        self.fields["conversation_language"].choices = choices
        self.fields["content_language"].choices = [("", _("Not editing content"))] + choices
        self.fields["content_block"].choices = [("", _("No content block context"))] + [
            (definition["key"], get_content_block_ui_label(definition["key"]))
            for definition in PILOT_CONTENT_BLOCK_DEFINITIONS
        ]


def _assistant_site_or_forbidden(request):
    site = assistant_site_for_request(request)
    if not user_can_access_assistant_site(request.user, site):
        return None
    return site


def _common_context(profile, section):
    return {
        "profile": profile,
        "active_section": section,
        "assistant_sections": ASSISTANT_SECTIONS,
        "supported_languages": [
            {"code": code, "label": assistant_language_label(code)}
            for code in SUPPORTED_LANGUAGES
        ],
        "capability_registry": ASSISTANT_CAPABILITIES,
    }


def assistant_dashboard(request, section="overview"):
    if section not in {item[0] for item in ASSISTANT_SECTIONS}:
        return redirect("control_panel:assistant")
    site = _assistant_site_or_forbidden(request)
    if not site:
        return HttpResponseForbidden(_("You do not have access to this assistant profile."))
    profile = ensure_assistant_profile(site)
    context = _common_context(profile, section)
    context["site"] = site
    context["section_template"] = f"controlpanel/assistant/{section}.html"

    if section == "overview":
        form = AssistantOverviewForm(
            request.POST or None,
            initial={
                "display_name": profile.display_name,
                "role": profile.role,
                "purpose": profile.purpose,
                "enabled": profile.enabled,
                "default_conversation_language": profile.default_conversation_language,
                "frontend_enabled": profile.frontend_enabled,
                "backend_enabled": profile.backend_enabled,
            },
        )
        if request.method == "POST" and form.is_valid():
            for field in ("display_name", "role", "purpose", "enabled", "default_conversation_language", "frontend_enabled", "backend_enabled"):
                setattr(profile, field, form.cleaned_data[field])
            profile.save()
            messages.success(request, _("Assistant profile saved."))
            return redirect("control_panel:assistant_section", section=section)
        context["form"] = form

    elif section == "business":
        form = AssistantBusinessForm(
            request.POST or None,
            initial={
                "business_description": profile.business_description,
                "business_facts": profile.business_facts,
                "business_rules": profile.business_rules,
            },
        )
        if request.method == "POST" and form.is_valid():
            profile.business_description = form.cleaned_data["business_description"]
            profile.business_facts = form.cleaned_data["business_facts"] or {}
            profile.business_rules = form.cleaned_data["business_rules"] or {}
            profile.save()
            messages.success(request, _("Business knowledge saved."))
            return redirect("control_panel:assistant_section", section=section)
        context["form"] = form

    elif section == "languages":
        configs = list(profile.language_configs.order_by("language_code"))
        if request.method == "POST":
            for config in configs:
                prefix = f"language_{config.language_code}_"
                config.enabled = request.POST.get(prefix + "enabled") == "on"
                config.greeting = request.POST.get(prefix + "greeting", "").strip()
                config.welcome_message = request.POST.get(prefix + "welcome_message", "").strip()
                config.fallback_message = request.POST.get(prefix + "fallback_message", "").strip()
                config.handoff_message = request.POST.get(prefix + "handoff_message", "").strip()
                config.save()
            profile.default_conversation_language = request.POST.get("default_conversation_language", profile.default_conversation_language)
            if profile.default_conversation_language not in SUPPORTED_LANGUAGES:
                profile.default_conversation_language = "nl"
            profile.save(update_fields=["default_conversation_language", "updated_at"])
            messages.success(request, _("Language messages saved."))
            return redirect("control_panel:assistant_section", section=section)
        context["language_configs"] = configs

    elif section == "capabilities":
        capabilities = list(profile.capabilities.order_by("key"))
        if request.method == "POST":
            for capability in capabilities:
                capability.frontend_enabled = request.POST.get(f"frontend_{capability.key}") == "on"
                capability.backend_enabled = request.POST.get(f"backend_{capability.key}") == "on"
                capability.save()
            messages.success(request, _("Assistant capabilities saved."))
            return redirect("control_panel:assistant_section", section=section)
        context["capabilities"] = [
            {"record": capability, "definition": ASSISTANT_CAPABILITIES.get(capability.key, {})}
            for capability in capabilities
        ]

    elif section == "website_actions":
        context["website_action_capabilities"] = [
            capability for capability in profile.capabilities.all()
            if not capability.key.startswith("answer_")
        ]
        context["website_actions_read_only"] = True

    elif section == "test":
        session_key = f"assistant_test_thread:{site.id}"
        selection_key = f"assistant_test_selection:{site.id}"
        selection = request.session.get(selection_key, {})
        if request.method == "POST" and request.POST.get("action") == "clear":
            selection = {
                "surface": request.POST.get("surface") or selection.get("surface") or "backend",
                "conversation_language": request.POST.get("conversation_language") or selection.get("conversation_language") or profile.default_conversation_language,
                "content_language": request.POST.get("content_language") or selection.get("content_language") or "",
                "content_block": request.POST.get("content_block") or selection.get("content_block") or "",
            }
            request.session[selection_key] = selection
            request.session.pop(session_key, None)
            request.session.modified = True
            return redirect("control_panel:assistant_section", section=section)
        history = request.session.get(session_key, [])
        form = AssistantTestForm(request.POST or None, initial={
            "surface": selection.get("surface", "backend"),
            "conversation_language": selection.get("conversation_language", profile.default_conversation_language),
            "content_language": selection.get("content_language", ""),
            "content_block": selection.get("content_block", ""),
        })
        if request.method == "POST" and form.is_valid():
            try:
                response_text, assistant_context = request_assistant_response(
                    profile,
                    message=form.cleaned_data["message"],
                    conversation_language=form.cleaned_data["conversation_language"],
                    content_language=form.cleaned_data["content_language"] or None,
                    surface=form.cleaned_data["surface"],
                    content_block_key=form.cleaned_data["content_block"] or None,
                    history=history,
                )
            except AssistantServiceError as exc:
                messages.error(request, str(exc))
            else:
                history = (history + [
                    {"role": "user", "content": form.cleaned_data["message"].strip()},
                    {"role": "assistant", "content": response_text},
                ])[-12:]
                selection = {
                    "surface": form.cleaned_data["surface"],
                    "conversation_language": form.cleaned_data["conversation_language"],
                    "content_language": form.cleaned_data["content_language"] or "",
                    "content_block": form.cleaned_data["content_block"] or "",
                }
                request.session[session_key] = history
                request.session[selection_key] = selection
                request.session.modified = True
                context["test_response"] = response_text
                context["assistant_context"] = assistant_context
        context["conversation_history"] = history
        context["test_selection"] = selection
        context["form"] = form
        context["test_is_non_destructive"] = True
    return render(request, "controlpanel/assistant/base.html", context)

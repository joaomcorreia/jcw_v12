from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from core.content_blocks import get_content_block_ui_label, get_supported_content_languages
from core.models import ContentBlock, Site
from core.services.content_translations import ensure_content_site_settings, ensure_pilot_content_blocks, get_block_payload, get_block_summaries, get_translation, save_block_translation, update_site_translations


def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


class ContentSettingsForm(forms.Form):
    auto_translate_updates = forms.BooleanField(required=False, label=_("Automatic translation updates"))


class ContentBlockTranslationForm(forms.Form):
    eyebrow = forms.CharField(label=_("Section label"), max_length=200, required=False)
    heading = forms.CharField(label=_("Heading"), max_length=240)
    intro = forms.CharField(label=_("Introduction"), widget=forms.Textarea(attrs={"rows": 4}))
    item_1_title = forms.CharField(label=_("Card 1 title"), max_length=200)
    item_1_body = forms.CharField(label=_("Card 1 text"), widget=forms.Textarea(attrs={"rows": 3}))
    item_2_title = forms.CharField(label=_("Card 2 title"), max_length=200)
    item_2_body = forms.CharField(label=_("Card 2 text"), widget=forms.Textarea(attrs={"rows": 3}))
    item_3_title = forms.CharField(label=_("Card 3 title"), max_length=200)
    item_3_body = forms.CharField(label=_("Card 3 text"), widget=forms.Textarea(attrs={"rows": 3}))
    is_protected = forms.BooleanField(required=False, label=_("Protect this translation from automatic updates"))
    is_published = forms.BooleanField(required=False, initial=True, label=_("Published"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "dashboard-input")
        for name in ("intro", "item_1_body", "item_2_body", "item_3_body"):
            self.fields[name].widget.attrs["class"] = "dashboard-textarea"

    @classmethod
    def initial_from_payload(cls, payload, is_protected=False, is_published=True):
        items = list(payload.get("items", []))
        while len(items) < 3:
            items.append({"title": "", "body": ""})
        return {
            "eyebrow": payload.get("eyebrow", ""),
            "heading": payload.get("heading", ""),
            "intro": payload.get("intro", ""),
            "item_1_title": items[0].get("title", ""),
            "item_1_body": items[0].get("body", ""),
            "item_2_title": items[1].get("title", ""),
            "item_2_body": items[1].get("body", ""),
            "item_3_title": items[2].get("title", ""),
            "item_3_body": items[2].get("body", ""),
            "is_protected": is_protected,
            "is_published": is_published,
        }

    def build_payload(self):
        return {
            "eyebrow": self.cleaned_data["eyebrow"],
            "heading": self.cleaned_data["heading"],
            "intro": self.cleaned_data["intro"],
            "items": [
                {"title": self.cleaned_data["item_1_title"], "body": self.cleaned_data["item_1_body"]},
                {"title": self.cleaned_data["item_2_title"], "body": self.cleaned_data["item_2_body"]},
                {"title": self.cleaned_data["item_3_title"], "body": self.cleaned_data["item_3_body"]},
            ],
        }


def _get_main_site():
    return Site.objects.filter(is_main=True).first()


@staff_required
def content_translations(request):
    site = _get_main_site()
    if not site:
        messages.error(request, _("Main site not found. Run seed_pages first."))
        return redirect("control_panel:home")
    ensure_pilot_content_blocks(site)
    settings_obj = ensure_content_site_settings(site)

    if request.method == "POST":
        action = request.POST.get("action") or "settings"
        if action == "settings":
            form = ContentSettingsForm(request.POST)
            if form.is_valid():
                settings_obj.auto_translate_updates = form.cleaned_data["auto_translate_updates"]
                settings_obj.save(update_fields=["auto_translate_updates", "updated_at"])
                messages.success(request, _("Automatic translation updates setting saved."))
                return redirect("control_panel:content_translations")
        elif action == "update_translations":
            result = update_site_translations(site)
            if result["backend_available"]:
                messages.success(request, _("Translations updated for %(count)s language entries.") % {"count": len(result["updated"])})
            else:
                messages.warning(request, _("Automatic translation backend is not configured yet. Outdated translations were left unchanged."))
            return redirect("control_panel:content_translations")
    else:
        form = ContentSettingsForm(initial={"auto_translate_updates": settings_obj.auto_translate_updates})

    return render(request, "controlpanel/content_translations.html", {
        "settings_form": form,
        "content_settings": settings_obj,
        "block_summaries": get_block_summaries(site),
    })


@staff_required
def content_translation_edit(request, block_id, language_code):
    site = _get_main_site()
    if not site:
        messages.error(request, _("Main site not found. Run seed_pages first."))
        return redirect("control_panel:home")
    ensure_pilot_content_blocks(site)
    if language_code not in get_supported_content_languages():
        messages.error(request, _("Unsupported language."))
        return redirect("control_panel:content_translations")

    block = get_object_or_404(ContentBlock.objects.prefetch_related("translations"), pk=block_id, site=site)
    translation = get_translation(block, language_code, create=True)
    payload = get_block_payload(block, language_code)

    if request.method == "POST":
        form = ContentBlockTranslationForm(request.POST)
        if form.is_valid():
            result = save_block_translation(
                block,
                language_code,
                form.build_payload(),
                is_protected=form.cleaned_data["is_protected"],
                is_published=form.cleaned_data["is_published"],
                auto_translate_enabled=site.content_settings.auto_translate_updates,
            )
            auto_result = result["auto_result"]
            if site.content_settings.auto_translate_updates and auto_result["backend_available"]:
                if auto_result["failed_languages"]:
                    messages.warning(request, _("Content saved. %(count)s translation(s) updated; %(failed)s could not be updated and remain marked for review.") % {"count": len(auto_result["updated_languages"]), "failed": len(auto_result["failed_languages"])})
                else:
                    messages.success(request, _("Content saved. Automatic updates ran for %(count)s translation(s).") % {"count": len(auto_result["updated_languages"])})
            elif site.content_settings.auto_translate_updates:
                messages.warning(request, _("Content saved. Other translations were marked outdated because no automatic translation backend is configured yet."))
            else:
                messages.success(request, _("Content saved. Other translations were marked outdated."))
            return redirect("control_panel:content_translation_edit", block_id=block.id, language_code=language_code)
    else:
        form = ContentBlockTranslationForm(initial=ContentBlockTranslationForm.initial_from_payload(payload, is_protected=translation.is_protected, is_published=translation.is_published))

    return render(request, "controlpanel/content_translation_edit.html", {
        "block": block,
        "block_label": get_content_block_ui_label(block.key),
        "language_code": language_code,
        "source_language": (block.last_source_language or "en").upper(),
        "form": form,
        "translation": translation,
        "all_translations": block.translations.order_by("language_code"),
        "content_settings": site.content_settings,
        "back_url": reverse("control_panel:content_translations"),
    })

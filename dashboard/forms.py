from django import forms
from django.utils.translation import gettext_lazy as _


class HeroContentForm(forms.Form):
    title = forms.CharField(
        label=_("Title"),
        required=True,
        widget=forms.TextInput(attrs={"class": "dashboard-input"}),
    )
    subtitle = forms.CharField(
        label=_("Subtitle"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "class": "dashboard-input"}),
    )
    cta_text = forms.CharField(
        label=_("CTA text"),
        required=False,
        widget=forms.TextInput(attrs={"class": "dashboard-input"}),
    )
    cta_url = forms.CharField(
        label=_("CTA URL"),
        required=False,
        widget=forms.TextInput(attrs={"class": "dashboard-input"}),
    )

    def clean_cta_url(self):
        value = (self.cleaned_data.get("cta_url") or "").strip()
        if value and not (value.startswith("/") or value.startswith("http")):
            raise forms.ValidationError(
                _("CTA URL must start with / or http.")
            )
        return value


class PageSEOForm(forms.Form):
    meta_title = forms.CharField(
        label=_("Meta title"),
        required=False,
        max_length=70,
        widget=forms.TextInput(attrs={"class": "dashboard-input"}),
    )
    meta_description = forms.CharField(
        label=_("Meta description"),
        required=False,
        max_length=160,
        widget=forms.Textarea(attrs={"rows": 4, "class": "dashboard-input"}),
    )
    noindex = forms.BooleanField(label=_("Noindex"), required=False)

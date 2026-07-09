from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import BusinessProfile

INPUT_CLASS = "w-full rounded-lg border border-slate-300 px-3 py-2"
TEXTAREA_CLASS = "w-full rounded-lg border border-slate-300 px-3 py-2"


class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            "business_name",
            "category",
            "city",
            "country",
            "phone",
            "email_public",
            "website_goal",
            "brand_color",
        ]
        labels = {
            "business_name": _("Business name"),
            "category": _("Category"),
            "city": _("City"),
            "country": _("Country"),
            "phone": _("Phone"),
            "email_public": _("Public email"),
            "website_goal": _("Website goal"),
            "brand_color": _("Brand color"),
        }
        help_texts = {
            "website_goal": _("What should this website help you achieve?"),
            "brand_color": _("Optional. Example: #1D4ED8"),
        }
        widgets = {
            "business_name": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "category": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "city": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "country": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "phone": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "email_public": forms.EmailInput(attrs={"class": INPUT_CLASS}),
            "website_goal": forms.Textarea(attrs={"rows": 3, "class": TEXTAREA_CLASS}),
            "brand_color": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "#1D4ED8"}),
        }

    def clean_brand_color(self):
        value = (self.cleaned_data.get("brand_color") or "").strip()
        if not value:
            return ""
        if not value.startswith("#") or len(value) not in {4, 7}:
            raise forms.ValidationError(_("Please enter a valid color value like #1D4ED8."))
        return value

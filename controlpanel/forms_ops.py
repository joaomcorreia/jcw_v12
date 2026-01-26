from django import forms

from core.data.eu_locations import COUNTRIES
from core.models import Plan, SiteVisibility
from core.services.visibility import normalize_city, normalize_country


def _country_choices():
    return [(normalize_country(item["code"]), item["name"]) for item in COUNTRIES]


def _city_choices():
    choices = []
    for country in COUNTRIES:
        country_code = normalize_country(country.get("code"))
        for city in country.get("cities", []):
            city_slug = normalize_city(city)
            label = f"{city} ({country.get('name')})"
            choices.append((f"{country_code}|{city_slug}", label))
    return choices


class SitePlanForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=Plan.objects.filter(is_active=True).order_by("key"),
        required=False,
        empty_label="(Default)",
    )

    def __init__(self, *args, **kwargs):
        site = kwargs.pop("site", None)
        super().__init__(*args, **kwargs)
        if site:
            self.fields["plan"].initial = site.plan_id
        self.fields["plan"].widget.attrs.setdefault("class", "ops-input")


class SiteVisibilityForm(forms.Form):
    visibility_mode = forms.ChoiceField(
        choices=SiteVisibility.MODE_CHOICES,
        required=False,
    )
    countries = forms.MultipleChoiceField(
        choices=_country_choices(),
        required=False,
    )
    cities = forms.MultipleChoiceField(
        choices=_city_choices(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        allow_mode_change = kwargs.pop("allow_mode_change", True)
        initial_countries = kwargs.pop("initial_countries", None)
        initial_cities = kwargs.pop("initial_cities", None)
        super().__init__(*args, **kwargs)
        if not allow_mode_change:
            self.fields["visibility_mode"].disabled = True
        self.fields["visibility_mode"].widget.attrs.setdefault("class", "ops-select")
        if initial_countries is not None:
            self.fields["countries"].initial = initial_countries
        if initial_cities is not None:
            self.fields["cities"].initial = initial_cities

    def clean(self):
        cleaned = super().clean()
        countries = [
            normalize_country(code) for code in cleaned.get("countries", []) if code
        ]
        city_entries = []
        for raw in cleaned.get("cities", []):
            if "|" not in raw:
                continue
            country_code, city = raw.split("|", 1)
            country_code = normalize_country(country_code)
            city = normalize_city(city)
            if country_code not in countries:
                continue
            city_entries.append({"country": country_code, "city": city})
        cleaned["allowed_countries"] = countries
        cleaned["allowed_cities"] = city_entries
        return cleaned

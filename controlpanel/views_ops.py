from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from core.data.eu_locations import COUNTRIES
from core.models import Plan, Site
from core.services.visibility import normalize_city, normalize_country
from core.visibility_rules import sync_visibility_from_plan
from .forms_ops import SitePlanForm, SiteVisibilityForm


def _build_visibility_selection(visibility):
    selected_countries = [
        normalize_country(code) for code in (visibility.allowed_countries or [])
    ]
    selected_cities = []
    for entry in visibility.allowed_cities or []:
        if not isinstance(entry, dict):
            continue
        country = normalize_country(entry.get("country"))
        city = normalize_city(entry.get("city"))
        if country and city:
            selected_cities.append({"country": country, "city": city})
    selected_city_keys = {
        f"{item['country']}|{item['city']}" for item in selected_cities
    }
    initial_cities = list(selected_city_keys)
    return selected_countries, selected_cities, selected_city_keys, initial_cities


@staff_member_required
def ops_home(request):
    context = {
        "site_count": Site.objects.count(),
        "plan_count": Plan.objects.count(),
    }
    return render(request, "ops/home.html", context)


@staff_member_required
def ops_sites_list(request):
    sites = Site.objects.select_related("owner", "plan").order_by("-created_at")
    return render(request, "ops/sites_list.html", {"sites": sites})


@staff_member_required
def ops_site_detail(request, site_id):
    site = get_object_or_404(Site.objects.select_related("owner", "plan"), id=site_id)
    visibility = sync_visibility_from_plan(site)
    allow_mode_change = visibility.is_manual_override

    (
        selected_countries,
        selected_cities,
        selected_city_keys,
        initial_cities,
    ) = _build_visibility_selection(visibility)

    plan_form = SitePlanForm(site=site)
    visibility_form = SiteVisibilityForm(
        allow_mode_change=allow_mode_change,
        initial_countries=selected_countries,
        initial_cities=initial_cities,
        initial={"visibility_mode": visibility.visibility_mode},
    )

    if request.method == "POST":
        if "save_plan" in request.POST:
            plan_form = SitePlanForm(request.POST, site=site)
            if plan_form.is_valid():
                site.plan = plan_form.cleaned_data["plan"]
                site.save(update_fields=["plan"])
                sync_visibility_from_plan(site, force=True)
                messages.success(request, _("Plan updated for this site."))
                return redirect("ops:site_detail", site_id=site.id)
        elif "save_visibility" in request.POST:
            visibility_form = SiteVisibilityForm(
                request.POST,
                allow_mode_change=allow_mode_change,
            )
            if visibility_form.is_valid():
                visibility.allowed_countries = visibility_form.cleaned_data["allowed_countries"]
                visibility.allowed_cities = visibility_form.cleaned_data["allowed_cities"]
                if allow_mode_change:
                    mode = visibility_form.cleaned_data.get("visibility_mode")
                    if mode:
                        visibility.visibility_mode = mode
                visibility.save(
                    update_fields=[
                        "allowed_countries",
                        "allowed_cities",
                        "visibility_mode",
                        "last_updated",
                    ]
                )
                messages.success(request, _("Visibility settings updated."))
                return redirect("ops:site_detail", site_id=site.id)

            selected_countries = visibility_form.cleaned_data.get(
                "allowed_countries",
                visibility_form.data.getlist("countries"),
            )
            selected_cities = visibility_form.cleaned_data.get(
                "allowed_cities",
                [],
            )
            if not selected_cities:
                raw_city_keys = visibility_form.data.getlist("cities")
                for raw in raw_city_keys:
                    if "|" not in raw:
                        continue
                    country_code, city = raw.split("|", 1)
                    selected_cities.append(
                        {
                            "country": normalize_country(country_code),
                            "city": normalize_city(city),
                        }
                    )
            selected_city_keys = {
                f"{item.get('country')}|{item.get('city')}"
                for item in selected_cities
                if isinstance(item, dict)
            }

    lang = site.language or "en"
    dashboard_path = f"/{lang}/dashboard/"
    public_path = f"/{lang}/"
    dashboard_link = (
        reverse("ops:impersonate", args=[site.id]) + f"?next={dashboard_path}"
    )
    public_link = reverse("ops:impersonate", args=[site.id]) + f"?next={public_path}"

    mode_label_map = {
        "basic": _("Basic"),
        "locations": _("Locations"),
        "eu": _("EU"),
    }

    return render(
        request,
        "ops/site_detail.html",
        {
            "site": site,
            "visibility": visibility,
            "plan_form": plan_form,
            "visibility_form": visibility_form,
            "allow_mode_change": allow_mode_change,
            "visibility_mode_label": mode_label_map.get(visibility.visibility_mode, ""),
            "countries": COUNTRIES,
            "selected_countries": selected_countries,
            "selected_city_keys": selected_city_keys,
            "dashboard_link": dashboard_link,
            "public_link": public_link,
        },
    )


@staff_member_required
def ops_impersonate(request, site_id):
    site = Site.objects.filter(id=site_id).first()
    if site:
        request.session["impersonate_tenant_id"] = site.id
    next_url = request.GET.get("next") or reverse("core:dashboard")
    return redirect(next_url)


@staff_member_required
def ops_stop_impersonate(request):
    if "impersonate_tenant_id" in request.session:
        del request.session["impersonate_tenant_id"]
    return redirect("ops:sites")

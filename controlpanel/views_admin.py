from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template


TOOL_TEMPLATE_BY_SLUG = {
    "home": "controlpanel/home.html",
    "dashboard": "controlpanel/dashboard.html",
    "website-builder": "controlpanel/website_builder.html",
    "domains-hosting": "controlpanel/domains_hosting.html",
    "users": "controlpanel/users.html",
    "billing": "controlpanel/billing.html",
    "content-map": "controlpanel/content_map.html",
    "plans": "controlpanel/plans_list.html",
    "tenants": "controlpanel/tenants.html",
    "templates": "controlpanel/templates_list.html",
}


def _is_preview_mode(request):
    return request.user.is_superuser and request.GET.get("v") == "next"


def _resolve_tool_template(slug, preview_mode):
    base_template_name = TOOL_TEMPLATE_BY_SLUG.get(slug)
    if not base_template_name:
        raise Http404("Unknown admin tool")

    if not preview_mode:
        return base_template_name

    preview_template_name = f"admin_tools_next/{slug}.html"
    try:
        get_template(preview_template_name)
        return preview_template_name
    except TemplateDoesNotExist:
        return base_template_name


def _render_admin_tool(request, slug, context=None):
    preview_mode = _is_preview_mode(request)
    template_name = _resolve_tool_template(slug, preview_mode)
    final_context = dict(context or {})
    final_context["preview_mode"] = preview_mode
    final_context["preview_version"] = "next" if preview_mode else ""
    return render(request, template_name, final_context)


@staff_member_required
def admin_tool(request, slug):
    return _render_admin_tool(request, slug)

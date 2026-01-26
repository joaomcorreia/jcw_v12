from django.urls import path

from .views import (
    billing,
    dashboard,
    domains_hosting,
    home,
    plans_create,
    plans_edit,
    plans_freeze,
    plans_list,
    tenant_edit,
    tenant_impersonate,
    tenant_stop_impersonate,
    tenants,
    templates_create,
    templates_edit,
    templates_list,
    templates_toggle_publish,
    website_builder,
    content_map,
    users,
)

app_name = "control_panel"

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("website-builder/", website_builder, name="website_builder"),
    path("domains-hosting/", domains_hosting, name="domains_hosting"),
    path("templates/", templates_list, name="templates_list"),
    path("templates/new/", templates_create, name="templates_create"),
    path("templates/<int:template_id>/edit/", templates_edit, name="templates_edit"),
    path("templates/<int:template_id>/toggle/", templates_toggle_publish, name="templates_toggle_publish"),
    path("users/", users, name="users"),
    path("billing/", billing, name="billing"),
    path("content-map/", content_map, name="content_map"),
    path("plans/", plans_list, name="plans_list"),
    path("plans/create/", plans_create, name="plans_create"),
    path("plans/<int:plan_id>/edit/", plans_edit, name="plans_edit"),
    path("plans/<int:plan_id>/freeze/", plans_freeze, name="plans_freeze"),
    path("tenants/", tenants, name="tenants"),
    path("tenants/<int:tenant_id>/edit/", tenant_edit, name="tenant_edit"),
    path("tenants/<int:tenant_id>/impersonate/", tenant_impersonate, name="tenant_impersonate"),
    path("tenants/stop-impersonate/", tenant_stop_impersonate, name="tenant_stop_impersonate"),
]

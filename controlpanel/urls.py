from django.urls import path

from .views import (
    billing,
    dashboard,
    domains_hosting,
    home,
    tenant_impersonate,
    tenant_stop_impersonate,
    tenants,
    templates_create,
    templates_edit,
    templates_list,
    templates_toggle_publish,
    users,
)

app_name = "controlpanel"

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("domains-hosting/", domains_hosting, name="domains_hosting"),
    path("templates/", templates_list, name="templates_list"),
    path("templates/new/", templates_create, name="templates_create"),
    path("templates/<int:template_id>/edit/", templates_edit, name="templates_edit"),
    path("templates/<int:template_id>/toggle/", templates_toggle_publish, name="templates_toggle_publish"),
    path("users/", users, name="users"),
    path("billing/", billing, name="billing"),
    path("tenants/", tenants, name="tenants"),
    path("tenants/<int:tenant_id>/impersonate/", tenant_impersonate, name="tenant_impersonate"),
    path("tenants/stop-impersonate/", tenant_stop_impersonate, name="tenant_stop_impersonate"),
]

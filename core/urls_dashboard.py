from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("home/", views.dashboard, name="dashboard_home"),
    path("users/", views.dashboard_users, name="dashboard_users"),
    path("frontend/pages/", views.dashboard_pages, name="dashboard_pages"),
    path("frontend/pages/create/", views.dashboard_create_page, name="dashboard_pages_create"),
    path("frontend/pages/home/create/", views.dashboard_create_home, name="create_home"),
    path("frontend/pages/<int:page_id>/edit/", views.dashboard_edit_page, name="page_edit"),
    path("frontend/content-map/", views.dashboard_content_map, name="content_map"),
    path(
        "frontend/pages/<int:page_id>/edit-services/",
        views.dashboard_edit_page_services,
        name="page_edit_services",
    ),
    path(
        "frontend/pages/<int:page_id>/edit-contact/",
        views.dashboard_edit_page_contact,
        name="page_edit_contact",
    ),
    path(
        "frontend/pages/<int:page_id>/seo/",
        views.dashboard_page_seo,
        name="page_seo",
    ),
    path("frontend/visibility/", views.dashboard_visibility, name="visibility"),
    path("frontend/menu/", views.dashboard_menu, name="menu"),
    path("frontend/site-settings/", views.dashboard_site_settings, name="site_settings"),
    path("api/inline-save/", views.dashboard_inline_save, name="inline_save"),
    path("api/section-settings/", views.dashboard_section_settings, name="section_settings"),
    path("main-site/pages/", views.dashboard_main_site_pages, name="main_site_pages"),
    path("main-site/pages/<int:page_id>/edit/", views.dashboard_main_site_edit_page, name="main_site_page_edit"),
    path("frontend/blog/", views.dashboard_blog, name="dashboard_blog"),
    path("billing/", views.dashboard_billing, name="dashboard_billing"),
    path("print-studio/", views.dashboard_print_studio, name="dashboard_print_studio"),
    path("marketplace/", views.marketplace_jcw, name="marketplace_jcw"),
    path("marketplace/printlab/", views.marketplace_printlab, name="marketplace_printlab"),
    path(
        "marketplace/card-payments/",
        views.marketplace_card_payments,
        name="marketplace_card_payments",
    ),
    path("control-panel/", views.dashboard_control_panel, name="dashboard_control_panel"),
    path("widgets-demo/", views.dashboard_widgets_demo, name="dashboard_widgets_demo"),
    path("choose-template/", views.dashboard_choose_template, name="dashboard_choose_template"),
    path("use-template/<int:template_id>/", views.dashboard_use_template, name="dashboard_use_template"),
    path("edit-home/", views.dashboard_edit_home, name="dashboard_edit_home"),
    path("reset-site/", views.dashboard_reset_site, name="dashboard_reset_site"),
]

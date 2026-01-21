from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard_home"),
    path("users/", views.dashboard_users, name="dashboard_users"),
    path("frontend/pages/", views.dashboard_pages, name="dashboard_pages"),
    path("frontend/pages/create/", views.dashboard_create_page, name="dashboard_pages_create"),
    path("frontend/pages/<int:page_id>/edit/", views.dashboard_edit_page, name="dashboard_edit_page"),
    path("frontend/blog/", views.dashboard_blog, name="dashboard_blog"),
    path("billing/", views.dashboard_billing, name="dashboard_billing"),
    path("print-studio/", views.dashboard_print_studio, name="dashboard_print_studio"),
    path("control-panel/", views.dashboard_control_panel, name="dashboard_control_panel"),
    path("widgets-demo/", views.dashboard_widgets_demo, name="dashboard_widgets_demo"),
    path("choose-template/", views.dashboard_choose_template, name="dashboard_choose_template"),
    path("use-template/<int:template_id>/", views.dashboard_use_template, name="dashboard_use_template"),
    path("edit-home/", views.dashboard_edit_home, name="dashboard_edit_home"),
    path("reset-site/", views.dashboard_reset_site, name="dashboard_reset_site"),
]

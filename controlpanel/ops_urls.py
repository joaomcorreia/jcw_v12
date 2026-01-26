from django.urls import path

from .views_ops import (
    ops_home,
    ops_impersonate,
    ops_site_detail,
    ops_sites_list,
    ops_stop_impersonate,
)

app_name = "ops"

urlpatterns = [
    path("", ops_home, name="home"),
    path("sites/", ops_sites_list, name="sites"),
    path("sites/<int:site_id>/", ops_site_detail, name="site_detail"),
    path("sites/<int:site_id>/impersonate/", ops_impersonate, name="impersonate"),
    path("sites/stop-impersonate/", ops_stop_impersonate, name="stop_impersonate"),
]

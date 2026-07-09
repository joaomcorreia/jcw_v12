from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.tenant_home, name="home"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("dashboard/website/preview/", views.website_preview, name="website_preview"),
    path("locations/<str:country>/", views.location_country, name="location_country"),
    path("locations/<str:country>/<slug:city>/", views.location_city, name="location_city"),
    path("<slug:slug>/", views.public_page, name="public_page"),
]

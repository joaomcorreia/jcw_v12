from django.urls import path

from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("post-login/", views.post_login_redirect, name="post_login_redirect"),
]

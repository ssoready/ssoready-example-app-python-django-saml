from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("saml-redirect", views.saml_redirect, name="saml_redirect"),
    path("ssoready-callback", views.ssoready_callback, name="ssoready_callback"),
]

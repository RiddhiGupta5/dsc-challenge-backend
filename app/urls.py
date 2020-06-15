from django.urls import path, include
from .views import (
    GoogleSignInView,
    LogoutView,
    UpdateInstaHandle,
)

from .admin_views import (
    AdminSignupView,
    AdminLoginView,
    AdminLogoutView,
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("login/", GoogleSignInView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("update_insta_handle/", UpdateInstaHandle.as_view()),
    path("admin_signup/", AdminSignupView.as_view()),
    path("admin_login/", AdminLoginView.as_view()),
    path("admin_logout/", AdminLogoutView.as_view()),
]
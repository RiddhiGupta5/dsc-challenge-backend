from django.urls import path, include
from .views import (
    GoogleSignInView,
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("login/", GoogleSignInView.as_view()),
]
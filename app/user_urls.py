from django.urls import path, include
from .views import (
    GoogleSignInView,
    LogoutView,
    UpdateInstaHandle,
)

from .user_QA_views import (
    DailyQAView,
    WeeklyQAView,
    LeaderBoardView,
    HistoryView
)
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("login/", GoogleSignInView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("update_insta_handle/", UpdateInstaHandle.as_view()),
    path("daily_question/", DailyQAView.as_view()),
    path("weekly_question/", WeeklyQAView.as_view()),
    path("leaderboard/", LeaderBoardView.as_view()),
    path("history_view/", HistoryView.as_view()),
]

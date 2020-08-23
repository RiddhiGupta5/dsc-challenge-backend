from django.urls import path, include

from .admin_views import (
    AdminSignupView,
    AdminLoginView,
    AdminLogoutView,
)

from .admin_QA_views import (
    QuestionView,
    AnswersView,
    AllQuestions,
    AllAnswers,
    AllUsers,
    FilterQuestions,
)

from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path("signup/", AdminSignupView.as_view()),
    path("login/", AdminLoginView.as_view()),
    path("logout/", AdminLogoutView.as_view()),
    path("add_question/", QuestionView.as_view()),
    path("unevaluated_answers/", AnswersView.as_view()),
    path("all_questions/", AllQuestions.as_view()),
    path("view_questions/<int:questionFilter>/", FilterQuestions.as_view()),
    path("all_answers/", AllAnswers.as_view()),
    path("view_all_users/", AllUsers.as_view()),
]

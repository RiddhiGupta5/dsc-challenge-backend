from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):

    # PLATFORM
    # 0 - App or website
    # 1 - Instagram

    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=50)
    platform = models.IntegerField(default=0)
    insta_handle = models.CharField(max_length=50, default=None, null=True)
    profile_image = models.URLField(null=True, default=None)
    # Field necessary for a django user
    is_staff = models.BooleanField(default=False)
    # Field necessary for a django user
    is_active = models.BooleanField(default=True)
    # Field necessary for a django user
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'insta_handle', 'platform', 'profile_image']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Question(models.Model):

    # QUESTION TYPE:
    # 0 - Daily Challenges
    # 1 - Weekly challenges

    question_body = models.TextField()
    display_date = models.DateTimeField(default=None, null=True)
    correct_answer = models.CharField(max_length=50, null=True)
    question_type = models.IntegerField()
    is_exact_match = models.BooleanField(default=False, null=True)
    creation_date_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creation_date_time']


class Answer(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_body = models.TextField()
    description = models.TextField(null=True)
    marks = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    evaluated = models.BooleanField(default=False)
    creation_date_time = models.DateTimeField(auto_now_add=True)

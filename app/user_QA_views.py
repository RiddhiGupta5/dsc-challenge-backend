import os
import datetime
import random

from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import authenticate, login, logout

from .models import User, Question, Answer
from .serializers import QuestionSerializer

class DailyQuestionView(APIView):

    def get(self, request):
        question_type = {
            'daily':0,
            'weekly':1
        }
        current_date = str(datetime.date.today()).split('-')
        # current_date = '2020-06-18'.split('-')
        year = current_date[0]
        month = current_date[1]
        day = current_date[2]
        question = Question.objects.filter(display_date__year=year, display_date__month=month, display_date__day=day, question_type=question_type['daily'])
        if len(question)==0:
            questions = Question.objects.filter(display_date=None, question_type=question_type['daily'])
            if len(questions)==0:
                return Response({"message":"No More Questions"}, status=status.HTTP_204_NO_CONTENT)
            index = random.randrange(0, len(questions), 1)
            selected_question = questions[index]
            selected_question.display_date = timezone.now()
            selected_question.save()
        else:
            selected_question = question[0]
        serializer = QuestionSerializer(selected_question)
        return Response({"message":"Question Found", "Question":serializer.data})


class WeeklyQuestionView(APIView):

    def get(self, request):
        question_type = {
            'daily':0,
            'weekly':1
        }
        DISPLAY_DAYS = 6
        start_date = timezone.now().date()
        # start_date = datetime.date(2020, 6, 23)
        end_date = start_date + datetime.timedelta( days= DISPLAY_DAYS) 
        print(start_date)
        print(end_date)
        question = Question.objects.filter(display_date__date__range=(start_date, end_date), question_type=question_type['weekly'])
        if len(question)==0:
            questions = Question.objects.filter(display_date=None, question_type=question_type['weekly'])
            if len(questions)==0:
                return Response({"message":"No More Questions"}, status=status.HTTP_204_NO_CONTENT)
            index = random.randrange(0, len(questions), 1)
            selected_question = questions[index]
            selected_question.display_date = timezone.now() + datetime.timedelta(days=DISPLAY_DAYS)
            selected_question.save()
        else:
            selected_question = question[0]
        serializer = QuestionSerializer(selected_question)
        return Response({"message":"Question Found", "Question":serializer.data})

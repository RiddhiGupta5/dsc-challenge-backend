import os
import datetime
import random
from fuzzywuzzy import fuzz

from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import authenticate, login, logout

from .models import User, Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer

class DailyQAView(APIView):

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
        serializer = serializer.data
        del serializer['correct_answer']
        return Response({"message":"Question Found", "Question":serializer})

    def post(self, request):

        # Marking Scheme
        CORRECT_MARKS = 10
        WRONG_MARKS = 0

        try:
            question = Question.objects.get(id=request.data.get('question_id'))
        except Question.DoesNotExist:
            return Response({"message":"Invalid Question Id"}, status=status.HTTP_400_BAD_REQUEST)
        
        if question.question_type!=0:
            return Response({"message":"Not a Daily Question"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = Answer.objects.get(user_id=request.user.id, question_id=question.id)
            return Response({"message":"Already Answered"}, status=status.HTTP_400_BAD_REQUEST)
        except Answer.DoesNotExist:
            if request.data.get('answer_body', None)==None:
                return Response({"message":"Answer Body is Empty"}, status=status.HTTP_400_BAD_REQUEST)
            if question.is_exact_match:
                if request.data['answer_body'] == question.correct_answer:
                    marks = CORRECT_MARKS
                else:
                    marks = WRONG_MARKS
            else:
                user_answer = request.data['answer_body']
                correct_answer = question.correct_answer
                match_percent = fuzz.token_set_ratio(user_answer, correct_answer)
                if match_percent >= 89:
                    marks = CORRECT_MARKS
                else:
                    marks = WRONG_MARKS
            
            answer = {
                "question_id":question.id,
                "answer_body":request.data['answer_body'],
                "description":request.data.get('description', None),
                "user_id":request.user.id,
                "marks":marks,
                "evaluated":True
            }

            serializer = AnswerSerializer(data=answer)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Answer Saved Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"Answer is Invalid"}, status=status.HTTP_400_BAD_REQUEST)

class WeeklyQAView(APIView):

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
        serializer = serializer.data
        del serializer['correct_answer']
        return Response({"message":"Question Found", "Question":serializer})

    def post(self, request):
        try:
            question = Question.objects.get(id=request.data.get('question_id'))
        except Question.DoesNotExist:
            return Response({"message":"Invalid Question Id"}, status=status.HTTP_400_BAD_REQUEST)
        
        if question.question_type!=1:
            return Response({"message":"Not a Weekly Question"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.get('answer_body', None)==None:
                return Response({"message":"Answer Body is Empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            answer = Answer.objects.get(user_id=request.user.id, question_id=question.id)
            answer.answer_body = request.data['answer_body']
            answer.save()
            return Response({"message":"Answered Updated"}, status=status.HTTP_400_BAD_REQUEST)
        except Answer.DoesNotExist:            
            answer = {
                "question_id":question.id,
                "answer_body":request.data['answer_body'],
                "description":request.data.get('description', None),
                "user_id":request.user.id
            }

            serializer = AnswerSerializer(data=answer)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Answer Saved Successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"Answer is Invalid"}, status=status.HTTP_400_BAD_REQUEST)

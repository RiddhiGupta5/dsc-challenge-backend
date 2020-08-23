import os
import pyexcel
import xlrd
from fuzzywuzzy import fuzz

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.exceptions import ParseError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.contrib.auth.base_user import BaseUserManager

from .models import Question, Answer, User
from .serializers import QuestionSerializer, AnswerSerializer, UserSerializer


class QuestionView(APIView):

    def post(self, request):
        if request.user.is_superuser:
            serializer = QuestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Question saved"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid question"}, )
        else:
            return Response({"message": "Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)


class AnswersView(APIView):

    def get(self, request):
        if request.user.is_superuser:
            answers = Answer.objects.filter(evaluated=False)
            serializer = AnswerSerializer(answers, many=True)
            if len(serializer.data) != 0:
                return Response({
                    "message": "Unevaluated Answers Found",
                    "Answer": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "No unevaluated Answers Found"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message": "Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        if request.user.is_superuser:
            try:
                answer = Answer.objects.get(
                    id=request.data.get('answer_id', None))
                if answer.evaluated:
                    return Response({"message": "Answer already evaluated"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    answer.evaluated = True
                    answer.marks = request.data.get('marks', 0)
                    answer.save()
                    return Response({"message": "Evaluated Answer"}, status=status.HTTP_200_OK)
            except Answer.DoesNotExist:
                return Response({"message": "Invalid Answer id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)


class AllAnswers(APIView):
    parser_class = (FileUploadParser,)

    def get(self, request):
        if request.user.is_superuser:
            answers = Answer.objects.all()
            serializer = AnswerSerializer(answers, many=True)
            return Response({"message": "All Answers Found", "Answers": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        CORRECT_MARKS = int(os.getenv('CORRECT_MARKS_INSTA'))
        WRONG_MARKS = int(os.getenv('WRONG_MARKS_INSTA'))

        if request.user.is_superuser:
            if 'answers_file' not in request.data:
                return Response({"message": "File Missing"}, status=status.HTTP_400_BAD_REQUEST)

            file = request.data['answers_file']
            extension = file.name.split('.')[-1]
            if extension not in ['csv', 'xls', 'xlsx']:
                return Response({"message": "Invalid File Format"}, status=status.HTTP_400_BAD_REQUEST)

            content = file.read()
            records = pyexcel.iget_records(
                file_type=extension, file_content=content)
            print("____________________________________________________________________")
            for record in records:

                username = record.get('username', None)
                answer_body = record.get('answer_body', None)
                daily_challenge = record.get('daily_challenge', None)
                marks = 0
                platform = 1

                if username == "" or answer_body == "" or daily_challenge == "":
                    print(
                        "LOGS: USER -> Username or answer_body or daily challenge missing")
                    continue

                try:
                    question = Question.objects.get(id=daily_challenge)
                except Question.DoesNotExist:
                    print("LOGS: QUESTION -> Question Not Found")
                    continue

                if question.is_exact_match:
                    if answer_body == question.correct_answer:
                        marks = CORRECT_MARKS
                    else:
                        marks = WRONG_MARKS
                else:
                    user_answer = answer_body
                    correct_answer = question.correct_answer
                    match_percent = fuzz.token_set_ratio(
                        user_answer, correct_answer)
                    if match_percent >= 89:
                        marks = CORRECT_MARKS
                    else:
                        marks = WRONG_MARKS

                user = User.objects.filter(insta_handle__iexact=username)
                if len(user) == 0:
                    user = User.objects.filter(
                        username__iexact=username, email=username+"@email.com")
                if len(user) != 0:
                    user = user[0]
                    answer = {
                        "answer_body": answer_body,
                        "question_id": daily_challenge,
                        "marks": marks,
                        "user_id": user.id,
                        "evaluated": True
                    }

                else:
                    user = User()
                    user.username = username
                    user.email = username+"@email.com"
                    user.password = make_password(
                        BaseUserManager().make_random_password())
                    user.platform = platform
                    user.profile_image = "https://freesvg.org/img/abstract-user-flat-4.png"
                    user.save()
                    print("LOGS: USER -> New User created username = " + username)
                    answer = {
                        "answer_body": answer_body,
                        "question_id": daily_challenge,
                        "marks": marks,
                        "user_id": user.id,
                        "evaluated": True
                    }

                try:
                    stored_answer = Answer.objects.get(
                        user_id=answer['user_id'], question_id=question.id)
                    print("LOGS: ANSWER -> Answer Already Stored for user " + username)

                except:
                    serializer = AnswerSerializer(data=answer)
                    if serializer.is_valid():
                        serializer.save()
                        print("LOGS: ANSWER -> Answer stored for " + username)
                    else:
                        print("LOGS: ANSWER -> Invalid Answer of " + username)

            print("____________________________________________________________________")
            return Response({"message": "Answers saved succesfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)


class AllUsers(APIView):
    def get(self, request):
        if request.user.is_superuser:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response({"message": "All Users Found", "Users": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)


class FilterQuestions(APIView):

    def get(self, request, questionFilter):
        if request.user.is_superuser:
            questions = Question.objects.filter(question_type=questionFilter)
            serializer = QuestionSerializer(questions, many=True)
            return Response({"message": "All Questions Found", "Questions": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)


class AllQuestions(APIView):
    parser_class = (FileUploadParser,)

    def get(self, request):
        if request.user.is_superuser:
            questions = Question.objects.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response({"message": "All Questions Found", "Questions": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        if request.user.is_superuser:

            if 'question_file' not in request.data:
                return Response({"message": "File Missing"}, status=status.HTTP_400_BAD_REQUEST)

            file = request.data['question_file']
            extension = file.name.split('.')[-1]
            if extension not in ['csv', 'xls', 'xlsx']:
                return Response({"message": "Invalid File Format"}, status=status.HTTP_400_BAD_REQUEST)

            content = file.read()
            records = pyexcel.iget_records(
                file_type=extension, file_content=content)
            print("____________________________________________________________________")
            for record in records:
                is_daily_question = record.get('is_daily_question', None)
                question_body = record.get('question_body', None)
                correct_answer = record.get('correct_answer', None)
                is_exact_match = record.get('is_exact_match', None)
                question = {}
                if is_daily_question == "" or question_body == "":
                    print("LOGS: Question -> Is Daily Question or Body Missing")
                    continue
                if is_daily_question:
                    if correct_answer == "" or is_exact_match == "":
                        print(
                            "LOGS: Daily Question -> Missing Correct Answer or Is Exact Field")
                        continue
                    else:
                        question = {
                            "question_type": 0,
                            "question_body": question_body,
                            "correct_answer": correct_answer,
                            "is_exact_match": is_exact_match,
                        }
                else:
                    question = {
                        "question_type": 1,
                        "question_body": question_body,
                    }
                serializer = QuestionSerializer(data=question)
                if serializer.is_valid():
                    serializer.save()
                    print("LOGS: Question -> Question Saved Successfully")
                else:
                    print("LOGS: Question -> Error: "+str(serializer.errors))
            print("____________________________________________________________________")

            return Response({"message": "All Questions Uploaded Successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)

import os

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import authenticate, login, logout

from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer

class QuestionView(APIView):

    def post(self, request):
        if request.user.is_superuser:
            serializer = QuestionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Question saved"}, status=status.HTTP_200_OK)
            else:
                return Response({"message":"Invalid question"}, )
        else:
            return Response({"message":"Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)

class AnswersView(APIView):

    def get(self, request):
        if request.user.is_superuser:
            answers = Answer.objects.filter(evaluated=False)
            serializer = AnswerSerializer(answers, many=True)
            if len(serializer.data)!=0:
                return Response({
                    "message":"Unevaluated Answers Found", 
                    "Answer": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message":"No unevaluated Answers Found"}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"message":"Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)
    
    def post(self, request):
        if request.user.is_superuser:
            try:
                answer = Answer.objects.get(id=request.data.get('answer_id', None))
                if answer.evaluated:
                    return Response({"message":"Answer already evaluated"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    answer.evaluated = True
                    answer.marks = request.data.get('marks', 0)
                    answer.save()
                    return Response({"message":"Evaluated Answer"}, status=status.HTTP_200_OK)
            except Answer.DoesNotExist:
                return Response({"message":"Invalid Answer id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message":"Only admin is allowed"}, status=status.HTTP_403_FORBIDDEN)
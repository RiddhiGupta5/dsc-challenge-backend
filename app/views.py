from google.auth.transport import requests
from google.oauth2 import id_token

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.conf import settings

from rest_framework import status
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User, Question, Answer


class GoogleSignInView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY

        try:
            idinfo = id_token.verify_oauth2_token(request.data['id_token'], requests.Request(), client_id)
        except Exception as error:
            return Response({"message": "Something went wrong"}, status=status.HTTP_403_FORBIDDEN)
        # print(idinfo['email'])
        # print(idinfo['name'])

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        try:
            user = User.objects.get(email=idinfo['email'])
        except User.DoesNotExist:
            user = User()
            user.username = idinfo['name']
            user.email = idinfo['email']
            user.password = make_password(BaseUserManager().make_random_password())
            user.save()
            
        token, _ = Token.objects.get_or_create(user=user)
        response = {
            'message': 'User Logged In',
            'User': {
                'id':user.id,
                'username': user.username,
                'email': user.email,
                'insta_handle': user.insta_handle,
                'platform': user.platform
            },
            'token': token.key
        }
        return Response(response, status=status.HTTP_200_OK)

class UpdateInstaHandle(APIView):

    def patch(self, request):
        user = request.user

        # Check and Update Insta Handle
        if (request.data.get('insta_handle', None)==None):
            return Response({"message":"Instagram Handle missing"}, status=status.HTTP_400_BAD_REQUEST)
        user.insta_handle = request.data['insta_handle']
        user.save()

        # Finding Insta Account if exists
        try:
            insta_user = User.objects.get(username=request.data['insta_handle'])

            # Transferring marks to new account and deleting the old one
            answers = Answer.objects.filter(user_id=insta_user.id)
            answer_to_delete = []
            for insta_answer in answers:
                # making sure that only one response for each question remains (One with more marks)
                try:
                    user_answer = Answer.objects.get(user_id=user.id, question_id=insta_answer.question_id)
                    if user_answer.marks > insta_answer.marks:
                        answer_to_delete.append(insta_answer)
                        continue
                    else:
                        user_answer.delete()
                except Answer.DoesNotExist:
                    pass 
                insta_answer.user_id = user
                insta_answer.save()

            insta_user.delete()
            for answer in answer_to_delete:
                answer.delete()
                
        except User.DoesNotExist:
            pass        

        return Response({"message":"Instagram Handle Updated Successfully"}, status=status.HTTP_200_OK)

# Signout new user
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        response = {
            "message":"User logged out", 
            "Details":{
                "id": user.id,
                "email":user.email,
                "username":user.username,
                'insta_handle': user.insta_handle,
                'platform': user.platform
            }}
        request.user.auth_token.delete()
        return Response(response, status=status.HTTP_200_OK)
        
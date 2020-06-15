import os

from google.auth.transport import requests
from google.oauth2 import id_token

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User

from dotenv import load_dotenv

load_dotenv()


class GoogleSignInView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        client_id = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
        idinfo = id_token.verify_oauth2_token(request.data['id_token'], requests.Request(), client_id)
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
                'username': user.username,
                'email': user.email,
                'insta_handle': user.insta_handle,
                'platform': user.platform
            },
            'token': token.key
        }
        return Response(response, status=status.HTTP_200_OK)


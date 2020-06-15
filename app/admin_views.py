import os

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import authenticate, login, logout

from .models import User, Question, Answer

# View for Admin Signup
class AdminSignupView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        req_data = {}
        req_data['email'] = request.data.get("email", None)
        req_data['username'] = request.data.get("username", None)
        req_data['password'] = request.data.get("password", None) 

        # Hardcoded the password and email address
        if (req_data.get('password', None)==os.getenv('ADMIN_PASSWORD') and 
            req_data.get('username', None)==os.getenv('ADMIN_USERNAME') and 
            req_data.get('email', None)==os.getenv('ADMIN_EMAIL_ID')):

            try:
                # Checking if Admin already signed up
                user = User.objects.get(email=req_data['email'])
                return Response({"message":"Admin already signed Up"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                # Creating superuser (Admin)
                User.objects.create_superuser(
                    email=req_data['email'],
                    username=req_data['username'],
                    password=req_data['password'],
                    insta_handle=None,
                    platform=0 
                )
                user = User.objects.get(email=req_data['email'])
                return Response({"message":"Admin Signed up"}, status=status.HTTP_400_BAD_REQUEST)

        else:            
            return Response({"message":"Invalid Email and Password"}, status=status.HTTP_400_BAD_REQUEST)

# View to Login Admin
class AdminLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        req_data = request.data
        user = authenticate(email=req_data['email'], password=req_data['password'])

        if not user:
            return Response({"message":"Invalid Details"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if user.is_superuser:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"message":"Admin Logged In", "token":token.key})
            else:
                return Response({"message":"Not an Admin"}, status=status.HTTP_400_BAD_REQUEST)


# View to Logout Admin
class AdminLogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        response = {"message":"Admin logged out"}
        request.user.auth_token.delete()
        return Response(response, status=status.HTTP_200_OK)
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from rest_framework import generics
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, LoginSerializer


class HomepageAPIView(APIView):

    def get(self, request):
        url_data = {
            'Signup': 'http://127.0.0.1:8000/signup',
            'Login': 'http://127.0.0.1:8000/login',
            'Logout': 'http://127.0.0.1:8000/logout',
            'Users': 'http://127.0.0.1:8000/users',

        }
        return Response(url_data, status=status.HTTP_200_OK)


class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserLogin(APIView):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({'error': 'User Already Authenticated'}, status=status.HTTP_400_BAD_REQUEST)
        data = {"username" : "" ,"password" : ""}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request,user)
        return Response({"message": "Login successful"}, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.COOKIES['auth_token'] = ''
        print(request.user)
        logout(request)
        response = Response("Logged out successfully.")
    
    # Redirect shortly
        response['Refresh'] = '3; url=/'  # Redirect to '/new-page/' after 3 seconds
    
        return response
        # return Response({'success': 'Logged out successfully'})

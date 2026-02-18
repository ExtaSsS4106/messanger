from django.contrib.auth.models import User

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserSerializer
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.authtoken.models import Token
import json

from main_app.models import *

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([]) 
def login_api(request):
    """
    {
        "username": "your_name",
        "password": "your_passwd"
    }
    """
    print("DATA",request.data['username'], request.data['password'])
    user = get_object_or_404(User, username=request.data['username'])
    serializer = UserSerializer(instance=user)
    if not user.check_password(request.data['password']):
        return Response({'detail':'not_found'}, status=status.HTTP_400_NOT_FOUND)
    token, created=Token.objects.get_or_create(user=user)
    
    return Response({"token": token.key, "user":serializer.data})

@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up_api(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.create(request.data)
        user = User.objects.get(username=request.data['username'])
        login(request, user)
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user":serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    try:
        request.user.auth_token.delete()
        return Response({'detail': 'Успешный выход'})
    except:
        return Response({'detail': 'Выполнен выход'})
 
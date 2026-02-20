from django.contrib.auth.models import User

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserSerializer
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.http import HttpResponse, JsonResponse

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
 
 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def select_friends(request):
    users_friends = Friends.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )
    
    friends_list = []
    for friendship in users_friends:
        friend = friendship.user2 if friendship.user1 == request.user else friendship.user1
        common_chat = Chat.objects.filter(
            users=request.user
        ).filter(
            users=friend
        ).first()
        
        friends_list.append({
            'id': friend.id,
            'username': friend.username,
            'email': friend.email,
            'chat_id': common_chat.id if common_chat else None
        })

    return JsonResponse({"friends_list": friends_list})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_messages(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        messages = Message.objects.filter(chat__id = chat_id).order_by('count')
        messages_list = []
        for msg in messages:
            messages_list.append({
                'id': msg.id,
                'count': msg.count,
                'user': msg.user.username if msg.user else 'Unknown',
                'text': msg.text,
                'type': msg.type,
                'file': msg.file.url if msg.file else None
            })
        return JsonResponse({"messages": messages_list})  
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])   
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        chat_id = data.get('chat_id')
        email = data.get('email')
        text = data.get('text')
        type = data.get('type')
        file = data.get('file')
        
        chat = Chat.objects.get(id=chat_id)
        user = User.objects.get(email=email)
        Message.objects.create(chat=chat, user=user, text=text, type=type, file=file)
        
        return HttpResponse(status=200)
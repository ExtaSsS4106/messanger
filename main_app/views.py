from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout
from .forms import RegisterForm
from django.contrib.auth.models import User
from .models import Friends, UserChat, Chat
from django.db.models import Q

# Авторизация\Регистрация

def index(request):
    return render(request, 'registration/index.html')

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return redirect('/')


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'registration/sign_up.html', {"form": form})


#Главная

@login_required()
def home(request):
    return render(request, 'main/main.html')

@login_required()
def add_friends(request):
    users = User.objects.all()
    l_users = []
    for user in users:
        exists = Friends.objects.filter(
            Q(user1=request.user, user2=user) |
            Q(user1=user, user2=request.user)
        ).exists()
        if not exists:
            l_users.append(user)
    
    return render(request, 'main/add-friends.html', {"users": l_users})


@login_required()
def add_new_friend(request, usr_id):
    if request.method == 'POST':
        new_fr = User.objects.get(id=usr_id)
        fr = Friends.objects.filter(user1=request.user, user2=new_fr)
        if fr.exists():
            return HttpResponse(status=204)
        try:
            Friends.objects.create(user1=request.user, user2=new_fr)
            new_chat = Chat.objects.create(type=Chat.PRIVATE)
            UserChat.objects.create(user=new_fr, chat=new_chat)
            UserChat.objects.create(user=request.user, chat=new_chat)
        except Exception as e:
            print(e)
        return HttpResponse("Success", status=200)
    
@login_required
def select_friends(request):
    users_friends = Friends.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    )
    
    friends_list = []
    for friendship in users_friends:
        friend = friendship.user2 if friendship.user1 == request.user else friendship.user1
        usrchat = UserChat.objects.filter(user=friend).filter(user=request.user).first
        friends_list.append({
            'id': friend.id,
            'username': friend.username,
            'email': friend.email,
            'chat_id': usrchat
        })

    return JsonResponse({"friends_list": friends_list})


@login_required
def open_chat(request):
    if request.method == 'POST':
        pass
    
    
@login_required()
def create_channel(request):
    if request.method == 'POST':
        pass
    return render(request, 'main/create-channel.html')





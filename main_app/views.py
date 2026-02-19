from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, get_user_model
from django.conf import settings
from .forms import CreateGroupChatForm
from .models import Chat, UserChat
from django.db import transaction

from .forms import RegisterForm
from .models import Friends, FriendRequest

User = get_user_model()

# Авторизация / Регистрация
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

# Главная
@login_required
def home(request):
    return render(request, 'main/home.html')

# Заявки в друзья
@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    # нельзя добавить себя
    if receiver == request.user:
        return redirect("home")

    # уже друзья?
    if Friends.objects.filter(
        user1=min(request.user, receiver, key=lambda u: u.id),
        user2=max(request.user, receiver, key=lambda u: u.id),
    ).exists():
        return redirect("home")

    # создаём заявку
    FriendRequest.objects.get_or_create(
        sender=request.user,
        receiver=receiver,
    )

    return redirect("home")


@login_required
def accept_friend_request(request, request_id):
    fr = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user,
    )

    fr.accept()
    return redirect("home")


@login_required
def decline_friend_request(request, request_id):
    fr = get_object_or_404(
        FriendRequest,
        id=request_id,
        receiver=request.user,
    )
    fr.delete()
    return redirect("home")

# Проверка дружбы
def are_friends(user_a, user_b):
    return Friends.objects.filter(
        user1=min(user_a, user_b, key=lambda u: u.id),
        user2=max(user_a, user_b, key=lambda u: u.id),
    ).exists()

# Удаление из друзей
@login_required
def remove_friend(request, user_id):
    user = request.user
    other_user = get_object_or_404(User, id=user_id)

    user1, user2 = sorted([user.id, other_user.id])

    friendship = get_object_or_404(
        Friends,
        user1_id=user1,
        user2_id=user2,
    )

    friendship.delete()

    # удалить приватный чат между ними
    private_chats = Chat.objects.filter(
        type=Chat.PRIVATE,
        users=user,
    ).filter(users=other_user)

    private_chats.delete()

    return redirect("home")

@login_required
def create_group_chat(request):
    if request.method == "POST":
        form = CreateGroupChatForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            users = form.cleaned_data["users"]

            with transaction.atomic():
                chat = Chat.objects.create(type=Chat.GROUP, name=name)

                # добавляем создателя + выбранных пользователей
                UserChat.objects.bulk_create(
                    [UserChat(user=request.user, chat=chat)] +
                    [UserChat(user=u, chat=chat) for u in users if u != request.user]
                )

            return redirect("home")
    else:
        form = CreateGroupChatForm()

    return render(request, "chat/create_group.html", {"form": form})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, get_user_model
from django.http import HttpResponse
from django.db import transaction
from .forms import CreateGroupChatForm, RegisterForm
from .models import Chat, UserChat, Message, Friends, FriendRequest

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
    if receiver == request.user:
        return redirect("home")
    if Friends.objects.filter(
        user1=min(request.user, receiver, key=lambda u: u.id),
        user2=max(request.user, receiver, key=lambda u: u.id),
    ).exists():
        return redirect("home")
    FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
    return redirect("home")

@login_required
def accept_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    fr.accept()
    return redirect("home")

@login_required
def decline_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    fr.delete()
    return redirect("home")

# Дружба
def are_friends(user_a, user_b):
    return Friends.objects.filter(
        user1=min(user_a, user_b, key=lambda u: u.id),
        user2=max(user_a, user_b, key=lambda u: u.id),
    ).exists()

@login_required
def remove_friend(request, user_id):
    user = request.user
    other_user = get_object_or_404(User, id=user_id)
    user1, user2 = sorted([user.id, other_user.id])
    friendship = get_object_or_404(Friends, user1_id=user1, user2_id=user2)
    friendship.delete()

    # удалить приватный чат между ними
    private_chats = Chat.objects.filter(type=Chat.PRIVATE, users=user).filter(users=other_user)
    private_chats.delete()
    return redirect("home")

# Создание группового чата
@login_required
def create_group_chat(request):
    if request.method == "POST":
        form = CreateGroupChatForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            users = form.cleaned_data["users"]
            with transaction.atomic():
                chat = Chat.objects.create(type=Chat.GROUP, name=name)
                UserChat.objects.bulk_create(
                    [UserChat(user=request.user, chat=chat)] +
                    [UserChat(user=u, chat=chat) for u in users if u != request.user]
                )
            return redirect("home")
    else:
        form = CreateGroupChatForm()
    return render(request, "chat/create_group.html", {"form": form})

# Просмотр чата и переписка
@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if not UserChat.objects.filter(user=request.user, chat=chat).exists():
        return HttpResponse("Вы не состоите в этом чате", status=403)

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        file = request.FILES.get("file")
        if text or file:
            msg_type = Message.TEXT if text else Message.FILE
            Message.objects.create(
                chat=chat,
                user=request.user,
                text=text if text else "",
                file=file if file else None,
                type=msg_type
            )
        return redirect("chat_detail", chat_id=chat.id)

    messages = chat.messages.select_related("user").order_by("id")
    return render(request, "chat/chat_detail.html", {"chat": chat, "messages": messages})

# Открыть приватный чат с пользователем
@login_required
def open_private_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect("home")

    # ищем существующий приватный чат
    chat = Chat.objects.filter(type=Chat.PRIVATE, users=request.user).filter(users=other_user).first()
    if not chat:
        with transaction.atomic():
            chat = Chat.objects.create(type=Chat.PRIVATE)
            UserChat.objects.bulk_create([
                UserChat(user=request.user, chat=chat),
                UserChat(user=other_user, chat=chat),
            ])
    return redirect("chat_detail", chat_id=chat.id)
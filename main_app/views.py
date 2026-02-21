from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, get_user_model
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.utils import timezone
from .forms import CreateGroupChatForm, RegisterForm
from .models import Chat, UserChat, Message, Friends, FriendRequest
from django.db import models
import json
import logging
import traceback

logger = logging.getLogger(__name__)

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
@login_required
def remove_friend_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            other_user = get_object_or_404(User, id=user_id)
            
            user1_id = min(request.user.id, other_user.id)
            user2_id = max(request.user.id, other_user.id)
            
            friendship = Friends.objects.get(
                user1_id=user1_id, 
                user2_id=user2_id
            )
            
            friendship.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Friend removed successfully'
            })
            
        except Friends.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Friendship not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

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
    fr.delete()
    return redirect("home")

@login_required
def decline_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    fr.delete()
    return redirect("home")

# Дружба
@login_required
def add_friend(request):
    users = User.objects.exclude(id=request.user.id)
    friend_ids = Friends.objects.filter(
        user1=request.user
    ).values_list("user2", flat=True)
    friend_ids2 = Friends.objects.filter(
        user2=request.user
    ).values_list("user1", flat=True)
    all_friend_ids = set(list(friend_ids) + list(friend_ids2))
    users = users.exclude(id__in=all_friend_ids)

    return render(request, "main/add_friend.html", {"users": users})
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
    # получаем список друзей пользователя
    friends_ids = Friends.objects.filter(
        user1=request.user
    ).values_list("user2", flat=True)

    friends_ids2 = Friends.objects.filter(
        user2=request.user
    ).values_list("user1", flat=True)

    friend_ids = list(friends_ids) + list(friends_ids2)
    friends = User.objects.filter(id__in=friend_ids)

    if request.method == "POST":
        form = CreateGroupChatForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"].strip()
            users = form.cleaned_data["users"]

            # защита: минимум 1 участник
            if not users:
                return render(request, "chat/create_group.html", {
                    "form": form,
                    "friends": friends,
                    "error": "Выберите хотя бы одного участника"
                })

            # защита: нельзя добавлять не-друзей
            for user in users:
                if user not in friends:
                    return HttpResponse("Можно добавлять только друзей", status=403)

            with transaction.atomic():
                chat = Chat.objects.create(
                    type=Chat.GROUP,
                    name=name if name else "Новый чат"
                )

                # добавляем создателя
                UserChat.objects.create(user=request.user, chat=chat)

                # добавляем выбранных пользователей
                UserChat.objects.bulk_create([
                    UserChat(user=u, chat=chat)
                    for u in users if u != request.user
                ])

            return redirect("chat_detail", chat_id=chat.id)

    else:
        form = CreateGroupChatForm()

    return render(request, "chat/create_group.html", {
        "form": form,
        "friends": friends
    })

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
                type=msg_type,
                created_at=timezone.now(),
                is_read=False,
                is_deleted=False
            )
            
            # Обновляем время последнего обновления чата
            chat.updated_at = timezone.now()
            chat.save(update_fields=['updated_at'])
            
        return redirect("chat_detail", chat_id=chat.id)

    # Получаем сообщения, исключая удаленные
    messages = chat.messages.filter(is_deleted=False).select_related("user").order_by("created_at")
    
    # Помечаем сообщения других пользователей как прочитанные
    messages.exclude(user=request.user).filter(is_read=False).update(is_read=True)
    
    return render(request, "chat/chat_detail.html", {
        "chat": chat, 
        "messages": messages
    })

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
            chat = Chat.objects.create(
                type=Chat.PRIVATE,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )
            UserChat.objects.bulk_create([
                UserChat(user=request.user, chat=chat),
                UserChat(user=other_user, chat=chat),
            ])
    return redirect("chat_detail", chat_id=chat.id)

"""@login_required
def add_friend(request):
    # получаем список всех пользователей, кроме текущего
    users = User.objects.exclude(id=request.user.id)

    # можно исключить уже друзей
    friend_ids = Friends.objects.filter(
        user1=request.user
    ).values_list("user2", flat=True)
    friend_ids2 = Friends.objects.filter(
        user2=request.user
    ).values_list("user1", flat=True)
    all_friend_ids = set(list(friend_ids) + list(friend_ids2))
    users = users.exclude(id__in=all_friend_ids)

    return render(request, "main/add_friend.html", {"users": users})
"""
# ========== ИСПРАВЛЕННЫЕ API VIEWS ==========
@login_required
def get_user_chats(request):
    """API: Получить список чатов пользователя"""
    try:
        chats = Chat.objects.filter(users=request.user).order_by('-updated_at')
        
        data = []
        for chat in chats:
            last_msg = chat.messages.filter(is_deleted=False).last()
            unread_count = chat.messages.exclude(user=request.user).filter(is_read=False).count()
            
            participants = chat.users.exclude(id=request.user.id)
            
            if chat.type == Chat.PRIVATE:
                other_user = participants.first()
                chat_name = other_user.username if other_user else 'Чат'
            else:
                chat_name = chat.name or 'Групповой чат'
            
            chat_data = {
                'id': chat.id,
                'type': chat.type,
                'chat_name': chat_name,
                'unread_count': unread_count,
                'updated_at': chat.updated_at.isoformat() if chat.updated_at else None,
                'participants': [{'id': u.id, 'username': u.username} for u in participants[:3]]
            }
            
            if last_msg:
                chat_data['last_message'] = {
                    'id': last_msg.id,
                    'text': last_msg.text[:50] + '...' if len(last_msg.text) > 50 else last_msg.text,
                    'username': last_msg.user.username if last_msg.user else 'Deleted',
                    'created_at': last_msg.created_at.isoformat() if last_msg.created_at else None,
                }
            else:
                chat_data['last_message'] = None
            
            data.append(chat_data)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_chat_messages(request, chat_id):
    """API: Получить сообщения чата"""
    try:
        chat = get_object_or_404(Chat, id=chat_id, users=request.user)
        
        messages = Message.objects.filter(
            chat=chat, 
            is_deleted=False
        ).select_related('user').order_by('created_at')
        
        messages.exclude(user=request.user).update(is_read=True)
        
        data = []
        for msg in messages:
            data.append({
                'id': msg.id,
                'user_id': msg.user.id if msg.user else None,
                'username': msg.user.username if msg.user else 'Deleted',
                'text': msg.text,
                'type': msg.type,
                'created_at': msg.created_at.isoformat() if msg.created_at else None,
                'is_read': msg.is_read,
            })
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def send_message_api(request, chat_id):
    """API: Отправить сообщение"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    try:
        chat = get_object_or_404(Chat, id=chat_id, users=request.user)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            text = data.get('text', '').strip()
        else:
            text = request.POST.get('text', '').strip()
        
        if not text:
            return JsonResponse({'error': 'Пустое сообщение'}, status=400)
        
        message = Message.objects.create(
            chat=chat,
            user=request.user,
            text=text,
            type=Message.TEXT,
            created_at=timezone.now(),
            is_read=False,
            is_deleted=False
        )
        
        chat.updated_at = message.created_at
        chat.save(update_fields=['updated_at'])
        
        return JsonResponse({
            'id': message.id,
            'user_id': request.user.id,
            'username': request.user.username,
            'text': message.text,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read,
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def search_users(request):
    """API: Поиск пользователей"""
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse([], safe=False)
        
        users = User.objects.filter(
            models.Q(username__icontains=query) |
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query)
        ).exclude(id=request.user.id)[:10]
        
        friend_ids = set()
        friendships = Friends.objects.filter(
            models.Q(user1=request.user) | models.Q(user2=request.user)
        )
        for f in friendships:
            if f.user1 == request.user:
                friend_ids.add(f.user2.id)
            else:
                friend_ids.add(f.user1.id)
        
        sent_requests = set(FriendRequest.objects.filter(
            sender=request.user, accepted=False
        ).values_list('receiver_id', flat=True))
        
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_friend': user.id in friend_ids,
                'has_pending_request': user.id in sent_requests,
            })
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_friends(request):
    """API: Получить список друзей"""
    try:
        friendships = Friends.objects.filter(
            models.Q(user1=request.user) | models.Q(user2=request.user)
        )
        
        friend_ids = []
        for f in friendships:
            if f.user1 == request.user:
                friend_ids.append(f.user2.id)
            else:
                friend_ids.append(f.user1.id)
        
        friends = User.objects.filter(id__in=friend_ids)
        
        data = [{
            'id': u.id,
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
        } for u in friends]
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_friend_requests(request):
    """API: Получить входящие заявки"""
    try:
        requests = FriendRequest.objects.filter(
            receiver=request.user, 
            accepted=False
        ).select_related('sender')
        
        data = []
        for req in requests:
            data.append({
                'id': req.id,
                'sender_id': req.sender.id,
                'sender_info': {
                    'id': req.sender.id,
                    'username': req.sender.username,
                    'first_name': req.sender.first_name,
                    'last_name': req.sender.last_name,
                },
                'created_at': req.created_at.isoformat() if req.created_at else None,
            })
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def send_friend_request_api(request):
    """API: Отправить заявку в друзья"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    try:
        data = json.loads(request.body)
        receiver_id = data.get('receiver_id')
        
        if not receiver_id:
            return JsonResponse({'error': 'Укажите получателя'}, status=400)
        
        if request.user.id == receiver_id:
            return JsonResponse({'error': 'Нельзя отправить заявку себе'}, status=400)
        
        receiver = get_object_or_404(User, id=receiver_id)
        
        # Проверяем, не друзья ли уже
        if Friends.objects.filter(
            models.Q(user1=request.user, user2=receiver) | 
            models.Q(user1=receiver, user2=request.user)
        ).exists():
            return JsonResponse({'error': 'Вы уже друзья'}, status=400)
        
        # Проверяем, нет ли уже заявки
        existing = FriendRequest.objects.filter(
            models.Q(sender=request.user, receiver=receiver) |
            models.Q(sender=receiver, receiver=request.user)
        ).filter(accepted=False).first()
        
        if existing:
            return JsonResponse({'error': 'Заявка уже существует'}, status=400)
        
        friend_request = FriendRequest.objects.create(
            sender=request.user,
            receiver=receiver
        )
        
        return JsonResponse({
            'id': friend_request.id,
            'status': 'sent'
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
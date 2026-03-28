from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, get_user_model
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import CreateGroupChatForm, RegisterForm, ProfileForm
from .models import Chat, UserChat, Message, Friends, FriendRequest, ChatInvite
from django.db import models
import json
import logging
import traceback
import os
import uuid
from datetime import timedelta
import qrcode
from io import BytesIO
import base64


logger = logging.getLogger(__name__)

User = get_user_model()

# Авторизация / Регистрация
def index(request):
    return render(request, 'registration/index.html')

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('/login')

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
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return render(request, "main/profile.html", {"form": form, "saved": True})
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "main/profile.html", {"form": form})

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
def create_group_chat(request):
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

            if not users:
                return render(request, "chat/create_group.html", {
                    "form": form,
                    "friends": friends,
                    "error": "Выберите хотя бы одного участника"
                })

            for user in users:
                if user not in friends:
                    return HttpResponse("Можно добавлять только друзей", status=403)

            with transaction.atomic():
                chat = Chat.objects.create(
                    type=Chat.GROUP,
                    name=name if name else "Новый чат"
                )

                UserChat.objects.create(user=request.user, chat=chat)

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

@login_required
def chat_detail(request, chat_id):
    return redirect(f'/home?chat={chat_id}')

@login_required
def open_private_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    if other_user == request.user:
        return redirect("home")

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
                message_data = {
                    'id': last_msg.id,
                    'text': last_msg.text[:50] + '...' if last_msg.text and len(last_msg.text) > 50 else (last_msg.text or ''),
                    'username': last_msg.user.username if last_msg.user else 'Deleted',
                    'created_at': last_msg.created_at.isoformat() if last_msg.created_at else None,
                    'type': last_msg.type,
                }
                
                if last_msg.file:
                    message_data['file_url'] = last_msg.file.url
                    message_data['file_name'] = os.path.basename(last_msg.file.name)
                    message_data['file_size'] = last_msg.file.size if hasattr(last_msg.file, 'size') else None
                    message_data['text'] = '📎 Файл'  # Заменяем текст на иконку файла
                
                chat_data['last_message'] = message_data
            else:
                chat_data['last_message'] = None
            
            data.append(chat_data)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Error in get_user_chats: {str(e)}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_chat_messages(request, chat_id):
    try:
        chat = get_object_or_404(Chat, id=chat_id, users=request.user)
        
        messages = Message.objects.filter(
            chat=chat, 
            is_deleted=False
        ).select_related('user').order_by('created_at')
        
        messages.exclude(user=request.user).update(is_read=True)
        
        data = []
        for msg in messages:
            message_data = {
                'id': msg.id,
                'user_id': msg.user.id if msg.user else None,
                'username': msg.user.username if msg.user else 'Deleted',
                'text': msg.text,
                'type': msg.type,
                'created_at': msg.created_at.isoformat() if msg.created_at else None,
                'is_read': msg.is_read,
            }
            
            if msg.file:
                message_data['file_url'] = msg.file.url
                message_data['file_name'] = os.path.basename(msg.file.name)
                message_data['file_size'] = msg.file.size if hasattr(msg.file, 'size') else None
                message_data['type'] = 'file'
            
            data.append(message_data)
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(f"Error in get_chat_messages: {str(e)}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def send_message_api(request, chat_id):
    """API: Отправить сообщение"""
    import json
    from django.utils import timezone
    
    print(f"\n=== SEND MESSAGE API ===")
    print(f"Method: {request.method}")
    print(f"Content-Type: {request.content_type}")
    print(f"Body: {request.body}")
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    try:
        chat = get_object_or_404(Chat, id=chat_id, users=request.user)
        
        # Получаем данные из запроса (JSON или multipart)
        file_obj = None
        text = ''
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            file_obj = request.FILES.get('file')
            text = request.POST.get('text', '').strip()
        else:
            try:
                data = json.loads(request.body)
                text = data.get('text', '').strip()
            except:
                text = request.POST.get('text', '').strip()
                file_obj = request.FILES.get('file')
        
        if not text and not file_obj:
            return JsonResponse({'error': 'Пустое сообщение'}, status=400)
        
        # Создаем сообщение
        message = Message.objects.create(
            chat=chat,
            user=request.user,
            text=text,
            file=file_obj if file_obj else None,
            type=Message.FILE if file_obj else Message.TEXT,
            created_at=timezone.now(),
            is_read=False,
            is_deleted=False
        )
        
        # Обновляем время чата
        chat.updated_at = message.created_at
        chat.save(update_fields=['updated_at'])
        
        response = {
            'id': message.id,
            'user_id': request.user.id,
            'username': request.user.username,
            'text': message.text,
            'created_at': message.created_at.isoformat(),
        }

        if message.file:
            response['file_url'] = message.file.url
            response['file_name'] = os.path.basename(message.file.name)
            response['file_size'] = message.file.size if hasattr(message.file, 'size') else None
            response['type'] = 'file'

        return JsonResponse(response, status=201)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
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
        print(f"Error in search_users: {str(e)}")
        traceback.print_exc()
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
        print(f"Error in get_friends: {str(e)}")
        traceback.print_exc()
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
        print(f"Error in get_friend_requests: {str(e)}")
        traceback.print_exc()
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
        print(f"Error in send_friend_request_api: {str(e)}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def delete_chat_api(request, chat_id):
    """API: Удалить чат"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    try:
        chat = get_object_or_404(Chat, id=chat_id, users=request.user)
        
        # Проверяем, является ли пользователь участником чата
        if not UserChat.objects.filter(user=request.user, chat=chat).exists():
            return JsonResponse({'error': 'Вы не являетесь участником этого чата'}, status=403)
        
        # Удаляем связь пользователя с чатом
        UserChat.objects.filter(user=request.user, chat=chat).delete()
        
        # Проверяем, остались ли еще участники
        remaining_users = chat.users.count()
        
        message = ""
        if remaining_users == 0:
            # Если никого не осталось, удаляем чат полностью
            chat.delete()
            message = "Чат полностью удален"
        else:
            message = "Вы покинули чат"
        
        return JsonResponse({
            'status': 'ok', 
            'message': message,
            'chat_deleted': remaining_users == 0
        }, status=200)
        
    except Exception as e:
        print(f"Error deleting chat: {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def remove_friend_api(request, user_id):
    """API: Удалить пользователя из друзей"""
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    try:
        other_user = get_object_or_404(User, id=user_id)
        
        # Проверяем, что пользователи не пытаются удалить сами себя
        if request.user.id == other_user.id:
            return JsonResponse({'error': 'Нельзя удалить самого себя из друзей'}, status=400)
        
        # Находим и удаляем дружбу
        user1, user2 = sorted([request.user.id, other_user.id])
        
        try:
            friendship = Friends.objects.get(user1_id=user1, user2_id=user2)
            friendship.delete()
        except Friends.DoesNotExist:
            return JsonResponse({'error': 'Пользователь не является вашим другом'}, status=400)
        
        # Удаляем приватные чаты между пользователями
        private_chats = Chat.objects.filter(
            type=Chat.PRIVATE,
            users=request.user
        ).filter(users=other_user)
        
        for chat in private_chats:
            # Удаляем связь текущего пользователя с чатом
            UserChat.objects.filter(user=request.user, chat=chat).delete()
            
            # Если в чате не осталось участников, удаляем чат
            if chat.users.count() == 0:
                chat.delete()
        
        return JsonResponse({
            'status': 'ok', 
            'message': f'Пользователь {other_user.username} удален из друзей'
        }, status=200)
        
    except Exception as e:
        print(f"Error removing friend: {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def create_chat_api(request):
    """API: Создать новый чат или получить существующий"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)
    
    try:
        data = json.loads(request.body)
        chat_type = data.get('type', Chat.PRIVATE)
        name = data.get('name', '')
        user_ids = data.get('users', [])
        
        # Добавляем текущего пользователя
        if request.user.id not in user_ids:
            user_ids.append(request.user.id)
        
        # Для приватного чата проверяем существующий
        if chat_type == Chat.PRIVATE and len(user_ids) == 2:
            existing_chat = Chat.objects.filter(
                type=Chat.PRIVATE,
                users__in=user_ids
            ).annotate(user_count=models.Count('users')).filter(user_count=2).first()
            
            if existing_chat:
                return JsonResponse({
                    'id': existing_chat.id, 
                    'exists': True,
                    'message': 'Чат уже существует'
                })
        
        # Создаем новый чат
        chat = Chat.objects.create(type=chat_type, name=name)
        
        # Добавляем пользователей
        for user_id in user_ids:
            user = get_object_or_404(User, id=user_id)
            UserChat.objects.create(user=user, chat=chat)
        
        return JsonResponse({
            'id': chat.id,
            'type': chat.type,
            'name': chat.name,
            'created': True
        }, status=201)
        
    except Exception as e:
        print(f"Error creating chat: {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
    
@login_required
def remove_friend(request, user_id):
    """Удалить пользователя из друзей (обычный view)"""
    user = request.user
    other_user = get_object_or_404(User, id=user_id)
    
    # Проверяем, что пользователи не пытаются удалить сами себя
    if user.id == other_user.id:
        return redirect("home")
    
    # Находим и удаляем дружбу
    user1, user2 = sorted([user.id, other_user.id])
    
    try:
        friendship = Friends.objects.get(user1_id=user1, user2_id=user2)
        friendship.delete()
    except Friends.DoesNotExist:
        return redirect("home")
    
    # Удаляем приватный чат между ними
    private_chats = Chat.objects.filter(
        type=Chat.PRIVATE, 
        users=user
    ).filter(users=other_user)
    
    for chat in private_chats:
        # Удаляем связь текущего пользователя с чатом
        UserChat.objects.filter(user=user, chat=chat).delete()
        
        # Если в чате не осталось участников, удаляем чат
        if chat.users.count() == 0:
            chat.delete()
    
    return redirect("home")


@login_required
def create_chat_invite(request, chat_id):
    """Создать приглашение в чат"""
    chat = get_object_or_404(Chat, id=chat_id, users=request.user)
    
    if request.method == 'POST':
        try:
            expires_in = int(request.POST.get('expires_in', 24))  # часы
            max_uses = int(request.POST.get('max_uses', 0))
            
            code = str(uuid.uuid4()).replace('-', '')[:16]
            
            expires_at = timezone.now() + timedelta(hours=expires_in) if expires_in > 0 else None
            
            invite = ChatInvite.objects.create(
                chat=chat,
                creator=request.user,
                code=code,
                expires_at=expires_at,
                max_uses=max_uses,
                is_active=True
            )
            
            invite_url = request.build_absolute_uri(f'/join/{code}/')
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(invite_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return render(request, 'chat/invite_created.html', {
                'invite': invite,
                'invite_url': invite_url,
                'qr_code': qr_base64,
                'chat': chat
            })
            
        except Exception as e:
            return render(request, 'chat/create_invite.html', {
                'chat': chat,
                'error': str(e)
            })
    
    return render(request, 'chat/create_invite.html', {'chat': chat})

@login_required
def join_chat_by_code(request, code):
    try:
        invite = get_object_or_404(ChatInvite, code=code, is_active=True)
        
        if not invite.is_valid():
            return render(request, 'chat/invite_error.html', {
                'error': 'Приглашение недействительно или истекло'
            })
        
        if UserChat.objects.filter(user=request.user, chat=invite.chat).exists():
            return redirect('chat_detail', chat_id=invite.chat.id)
        
        with transaction.atomic():
            UserChat.objects.create(user=request.user, chat=invite.chat)
            invite.use()
        
        return redirect('chat_detail', chat_id=invite.chat.id)
        
    except ChatInvite.DoesNotExist:
        return render(request, 'chat/invite_error.html', {
            'error': 'Приглашение не найдено'
        })

@login_required
def chat_invites_list(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, users=request.user)
    invites = ChatInvite.objects.filter(chat=chat).order_by('-created_at')
    
    return render(request, 'chat/invites_list.html', {
        'chat': chat,
        'invites': invites
    })

@login_required
def deactivate_invite(request, invite_id):
    invite = get_object_or_404(ChatInvite, id=invite_id, creator=request.user)
    
    if request.method == 'POST':
        invite.is_active = False
        invite.save()
        return redirect('chat_invites_list', chat_id=invite.chat.id)
    
    return render(request, 'chat/deactivate_invite.html', {'invite': invite})

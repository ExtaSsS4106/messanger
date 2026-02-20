# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Chat, Message, UserChat, Friends, FriendRequest

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор сообщения"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'chat', 'user_id', 'username', 'text', 
            'file_url', 'type', 'created_at', 'is_read', 'is_deleted'
        ]
        read_only_fields = ['created_at', 'is_read', 'is_deleted']
    
    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None

class ChatListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка чатов"""
    last_message = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    chat_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = [
            'id', 'type', 'chat_name', 'last_message', 
            'participants', 'unread_count', 'created_at', 'updated_at'
        ]
    
    def get_chat_name(self, obj):
        """Получить название чата для отображения"""
        user = self.context['request'].user
        
        if obj.type == Chat.PRIVATE:
            # Для приватного чата показываем имя собеседника
            other_user = obj.users.exclude(id=user.id).first()
            return other_user.username if other_user else 'Чат'
        return obj.name or 'Групповой чат'
    
    def get_last_message(self, obj):
        """Получить последнее сообщение в чате"""
        last_msg = obj.messages.exclude(is_deleted=True).last()
        if last_msg:
            return {
                'id': last_msg.id,
                'text': last_msg.text[:50] + '...' if len(last_msg.text) > 50 else last_msg.text,
                'username': last_msg.user.username if last_msg.user else 'Deleted',
                'created_at': last_msg.created_at,
                'is_read': last_msg.is_read,
            }
        return None
    
    def get_participants(self, obj):
        """Получить участников чата"""
        users = obj.users.all()[:3]  # только первые 3 для превью
        return [{'id': u.id, 'username': u.username} for u in users]
    
    def get_unread_count(self, obj):
        """Получить количество непрочитанных сообщений"""
        user = self.context['request'].user
        return obj.messages.exclude(user=user).filter(is_read=False).count()

class ChatDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о чате"""
    participants = UserSerializer(source='users', many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ['id', 'type', 'name', 'participants', 'messages', 'created_at', 'updated_at']
    
    def get_messages(self, obj):
        """Получить сообщения чата"""
        messages = obj.messages.filter(is_deleted=False).select_related('user')[:50]
        return MessageSerializer(messages, many=True).data

class FriendRequestSerializer(serializers.ModelSerializer):
    """Сериализатор заявки в друзья"""
    sender_info = UserSerializer(source='sender', read_only=True)
    receiver_info = UserSerializer(source='receiver', read_only=True)
    
    class Meta:
        model = FriendRequest
        fields = [
            'id', 'sender', 'receiver', 'sender_info', 
            'receiver_info', 'created_at', 'accepted'
        ]
        read_only_fields = ['sender', 'created_at', 'accepted']

class FriendSerializer(serializers.ModelSerializer):
    """Сериализатор для друзей"""
    friend = serializers.SerializerMethodField()
    
    class Meta:
        model = Friends
        fields = ['id', 'friend', 'user1', 'user2']
    
    def get_friend(self, obj):
        """Получить данные друга относительно текущего пользователя"""
        user = self.context['request'].user
        if obj.user1 == user:
            friend_user = obj.user2
        else:
            friend_user = obj.user1
        return UserSerializer(friend_user).data
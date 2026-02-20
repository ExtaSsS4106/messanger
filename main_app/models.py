# models.py
from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
import uuid

class Friends(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='friendships1', on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='friendships2', on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_friendship'),
            models.CheckConstraint(
                condition=~models.Q(user1=models.F("user2")),
                name="no_self_friendship",  
            ),
        ]

    def save(self, *args, **kwargs):
        if self.user1_id == self.user2_id:
            raise ValueError("Пользователь не может добавить в друзья сам себя")
        if self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

class Chat(models.Model):
    PRIVATE = 'private'
    GROUP = 'group'
    CHAT_TYPES = [(PRIVATE, 'Private'), (GROUP, 'Group')]

    type = models.CharField(max_length=10, choices=CHAT_TYPES, default=PRIVATE)
    name = models.CharField(max_length=255, blank=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='UserChat', related_name='chats'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserChat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)  # когда пользователь последний раз читал чат

    class Meta:
        unique_together = ('user', 'chat')

class Message(models.Model):
    TEXT = 'text'
    FILE = 'file'
    TYPE_CHOICES = [(TEXT, 'Text'), (FILE, 'File')]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='messages'
    )
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='messages/', blank=True, null=True)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default=TEXT)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['chat', 'created_at']),
            models.Index(fields=['chat', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user}: {self.text[:50]}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

class FriendRequest(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="sent_friend_requests", on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="received_friend_requests", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sender", "receiver"], name="unique_friend_request"),
            models.CheckConstraint(
                condition=~models.Q(sender=models.F("receiver")),
                name="no_self_friend_request",
            ),
        ]

    def accept(self):
        if self.accepted:
            return

        with transaction.atomic():
            Friends.objects.get_or_create(
                user1=min(self.sender, self.receiver, key=lambda u: u.id),
                user2=max(self.sender, self.receiver, key=lambda u: u.id),
            )

            chat = Chat.objects.create(type=Chat.PRIVATE)
            UserChat.objects.bulk_create([
                UserChat(user=self.sender, chat=chat),
                UserChat(user=self.receiver, chat=chat),
            ])

            self.accepted = True
            self.save(update_fields=["accepted"])

class ChatInvite(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='invites')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_invites')
    code = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.IntegerField(default=0)  # 0 = безлимитно
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['chat', 'is_active']),
        ]
    
    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        return True
    
    def use(self):
        if self.is_valid():
            self.used_count += 1
            if self.max_uses > 0 and self.used_count >= self.max_uses:
                self.is_active = False
            self.save()
            return True
        return False
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('join_chat_by_code', kwargs={'code': self.code})
    
    def __str__(self):
        return f"Invite to {self.chat.name or 'chat'} by {self.creator.username}"
from django.db import models, transaction
from django.conf import settings

# ---------- Дружба ----------
class Friends(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships2', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_friendship'),
            models.CheckConstraint(check=~models.Q(user1=models.F('user2')), name='no_self_friend'),
        ]

    def save(self, *args, **kwargs):
        if self.user1_id == self.user2_id:
            raise ValueError("Пользователь не может добавить в друзья сам себя")
        # Всегда сохраняем меньший id первым для уникальности
        if self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

# ---------- Чаты ----------
class Chat(models.Model):
    PRIVATE = 'private'
    GROUP = 'group'
    CHAT_TYPES = [(PRIVATE, 'Private'), (GROUP, 'Group')]

    type = models.CharField(max_length=10, choices=CHAT_TYPES, default=PRIVATE)
    name = models.CharField(max_length=255, blank=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserChat', related_name='chats')

# Связь пользователь–чат
class UserChat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chat')

# Сообщения
class Message(models.Model):
    TEXT = 'text'
    FILE = 'file'
    TYPE_CHOICES = [(TEXT, 'Text'), (FILE, 'File')]

    count = models.IntegerField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='messages')
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='messages/', blank=True, null=True)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default=TEXT)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]
        ordering = ['count']
        
    def save(self, *args, **kwargs):
        if not self.pk:  
            last_message = Message.objects.filter(chat=self.chat).order_by('-count').first()
            if last_message:
                self.count = last_message.count + 1
            else:
                self.count = 1
        super().save(*args, **kwargs)

# ---------- Заявки в друзья ----------
class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_friend_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="received_friend_requests", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sender", "receiver"], name="unique_friend_request"),
            models.CheckConstraint(condition=~models.Q(sender=models.F("receiver")), name="no_self_request"),
        ]

    # Принять заявку
    def accept(self):
        if self.accepted:
            return

        with transaction.atomic():
            # Создаём связь дружбы
            Friends.objects.get_or_create(
                user1=min(self.sender, self.receiver, key=lambda u: u.id),
                user2=max(self.sender, self.receiver, key=lambda u: u.id),
            )

            # Создаём приватный чат между пользователями
            chat = Chat.objects.create(type=Chat.PRIVATE)
            UserChat.objects.bulk_create([
                UserChat(user=self.sender, chat=chat),
                UserChat(user=self.receiver, chat=chat),
            ])

            # Обновляем статус заявки
            self.accepted = True
            self.save(update_fields=["accepted"])
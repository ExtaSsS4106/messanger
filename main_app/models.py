from django.db import models
from django.conf import settings

class Friends(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friendships2', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique_friendship'),
            models.CheckConstraint(condition=~models.Q(user1=models.F('user2')), name='no_self_friend'),
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
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserChat', related_name='chats')

class UserChat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chat')

class Message(models.Model):
    TEXT = 'text'
    FILE = 'file'
    TYPE_CHOICES = [(TEXT, 'Text'), (FILE, 'File')]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='messages')
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='messages/', blank=True, null=True)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default=TEXT)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]
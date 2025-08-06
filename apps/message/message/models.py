from django.db import models
from django.utils import timezone
from core.authentication.models import User

class Chat(models.Model):
    TYPE_CHOICES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='private')
    participants = models.ManyToManyField(User, through='ChatUser', related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'
    
    def get_room_name(self):
        """Получить имя комнаты для WebSocket"""
        return f"chat_{self.id}"
    
    def get_other_participant(self, user):
        """Получить другого участника приватного чата"""
        if self.type == 'private':
            other_participants = self.participants.exclude(id=user.id)
            return other_participants.first()
        return None

class ChatUser(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('chat', 'user')
        verbose_name = 'Участник чата'
        verbose_name_plural = 'Участники чатов'

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        indexes = [
            models.Index(fields=['chat', 'timestamp']),
            models.Index(fields=['sender', 'timestamp']),
        ]
    
    def edit_message(self, new_text):
        """Редактировать сообщение"""
        self.text = new_text
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()
    
    def delete_message(self):
        """Удалить сообщение (мягкое удаление)"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def get_room_name(self):
        """Получить имя комнаты для WebSocket"""
        return self.chat.get_room_name()
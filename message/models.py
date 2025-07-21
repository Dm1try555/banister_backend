from django.db import models
from authentication.models import User

class Chat(models.Model):
    TYPE_CHOICES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    participants = models.ManyToManyField(User, through='ChatUser')
    created_at = models.DateTimeField(auto_now_add=True)

class ChatUser(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='message')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
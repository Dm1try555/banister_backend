from rest_framework import serializers
from .models import Chat, Message
from authentication.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'text', 'timestamp']

class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    message = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Chat
        fields = ['id', 'type', 'created_at', 'participants', 'message']
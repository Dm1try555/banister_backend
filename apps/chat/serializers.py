from rest_framework import serializers
from .models import ChatRoom, Message
from apps.authentication.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'sender', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'participants', 'is_private', 'created_at', 'last_message']
        read_only_fields = ['id', 'created_at']
    
    def get_last_message(self, obj):
        last_message = obj.messages.filter(is_deleted=False).first()
        if last_message:
            return MessageSerializer(last_message).data
        return None
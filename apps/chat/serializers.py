from core.base.common_imports import *
from core.error_handling import ErrorCode
from .models import ChatRoom, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'content', 'sender_username', 'created_at', 'updated_at', 'is_deleted']
        read_only_fields = ['id', 'sender_username', 'created_at', 'updated_at']

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content', 'room']

    def validate_content(self, value):
        if not value or len(value.strip()) == 0:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        
        if len(value) > 1000:  # Maximum message length
            ErrorCode.FIELD_TOO_LONG.raise_error()
        
        return value

class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['content']

    def validate_content(self, value):
        if not value or len(value.strip()) == 0:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        
        if len(value) > 1000:  # Maximum message length
            ErrorCode.FIELD_TOO_LONG.raise_error()
        
        return value

class ChatRoomSerializer(serializers.ModelSerializer):
    participants_count = serializers.IntegerField(source='participants.count', read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'participants_count', 'is_private', 'created_at', 'last_message']
        read_only_fields = ['id', 'participants_count', 'created_at']
    
    def get_last_message(self, obj):
        last_message = obj.messages.filter(is_deleted=False).first()
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content,
                'created_at': last_message.created_at
            }
        return None

class ChatRoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['name', 'is_private']

    def validate_name(self, value):
        if not value or len(value.strip()) == 0:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        
        if len(value) > 100:  # Maximum room name length
            ErrorCode.FIELD_TOO_LONG.raise_error()
        
        return value

class ChatRoomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['name', 'is_private']

    def validate_name(self, value):
        if not value or len(value.strip()) == 0:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        
        if len(value) > 100:  # Maximum room name length
            ErrorCode.FIELD_TOO_LONG.raise_error()
        
        return value
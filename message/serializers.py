from rest_framework import serializers
from .models import Chat, Message, ChatUser
from authentication.serializers import UserSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = [
            'id', 'chat', 'sender', 'sender_id', 'text', 'timestamp',
            'is_edited', 'edited_at', 'is_deleted', 'deleted_at'
        ]
        read_only_fields = ['sender', 'timestamp', 'is_edited', 'edited_at', 'is_deleted', 'deleted_at']
    
    def create(self, validated_data):
        # sender_id удаляется из validated_data, sender устанавливается автоматически
        validated_data.pop('sender_id', None)
        return super().create(validated_data)

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['chat', 'text']

class MessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['text']

class ChatUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatUser
        fields = ['user', 'joined_at', 'is_active']

class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = [
            'id', 'type', 'created_at', 'updated_at', 'participants',
            'messages', 'last_message', 'unread_count'
        ]
    
    def get_last_message(self, obj):
        """Получить последнее сообщение в чате"""
        last_message = obj.messages.filter(is_deleted=False).last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        """Получить количество непрочитанных сообщений"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Здесь можно добавить логику подсчета непрочитанных сообщений
            # Пока возвращаем 0
            return 0
        return 0

class ChatCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        help_text="Список ID участников чата"
    )
    
    class Meta:
        model = Chat
        fields = ['type', 'participant_ids']
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        chat = Chat.objects.create(**validated_data)
        
        # Добавляем участников
        for user_id in participant_ids:
            try:
                from authentication.models import User
                user = User.objects.get(id=user_id)
                ChatUser.objects.create(chat=chat, user=user)
            except User.DoesNotExist:
                pass
        
        return chat
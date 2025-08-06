from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Chat, Message, ChatUser
from core.authentication.models import User
import json

def get_or_create_private_chat(user1, user2):
    """
    Получить или создать приватный чат между двумя пользователями
    """
    # Ищем существующий приватный чат
    existing_chat = Chat.objects.filter(
        type='private',
        participants=user1
    ).filter(
        participants=user2
    ).first()
    
    if existing_chat:
        return existing_chat
    
    # Создаем новый приватный чат
    chat = Chat.objects.create(type='private')
    ChatUser.objects.create(chat=chat, user=user1)
    ChatUser.objects.create(chat=chat, user=user2)
    
    return chat

def create_group_chat(participants, chat_type='group'):
    """
    Создать групповой чат
    """
    chat = Chat.objects.create(type=chat_type)
    
    for user in participants:
        ChatUser.objects.create(chat=chat, user=user)
    
    return chat

def send_message_to_chat(chat_id, sender, text):
    """
    Отправить сообщение в чат и уведомить всех участников через WebSocket
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        message = Message.objects.create(
            chat=chat,
            sender=sender,
            text=text
        )
        
        # Отправляем сообщение через WebSocket
        channel_layer = get_channel_layer()
        room_name = f"chat_{chat_id}"
        
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'text': message.text,
                    'sender': {
                        'id': message.sender.id,
                        'username': message.sender.username,
                        'first_name': message.sender.first_name,
                        'last_name': message.sender.last_name,
                    },
                    'timestamp': message.timestamp.isoformat(),
                    'is_edited': message.is_edited,
                    'is_deleted': message.is_deleted,
                }
            }
        )
        
        return message
        
    except Chat.DoesNotExist:
        raise ValueError(f"Chat with id {chat_id} does not exist")
    except Exception as e:
        raise Exception(f"Error sending message: {str(e)}")

def get_user_chats(user):
    """
    Получить все чаты пользователя
    """
    return Chat.objects.filter(participants=user).order_by('-updated_at')

def get_chat_messages(chat_id, user, page=1, page_size=50):
    """
    Получить сообщения чата с пагинацией
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        
        # Проверяем права доступа
        if user not in chat.participants.all():
            raise PermissionError("User does not have access to this chat")
        
        messages = Message.objects.filter(
            chat=chat,
            is_deleted=False
        ).order_by('-timestamp')
        
        # Применяем пагинацию
        start = (page - 1) * page_size
        end = start + page_size
        messages = messages[start:end]
        
        return messages
        
    except Chat.DoesNotExist:
        raise ValueError(f"Chat with id {chat_id} does not exist")

def edit_message(message_id, user, new_text):
    """
    Редактировать сообщение
    """
    try:
        message = Message.objects.get(id=message_id, is_deleted=False)
        
        # Проверяем права на редактирование
        if message.sender != user:
            raise PermissionError("User can only edit their own messages")
        
        message.edit_message(new_text)
        
        # Уведомляем через WebSocket
        channel_layer = get_channel_layer()
        room_name = f"chat_{message.chat.id}"
        
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'message_edited',
                'message': {
                    'id': message.id,
                    'text': message.text,
                    'is_edited': message.is_edited,
                    'edited_at': message.edited_at.isoformat() if message.edited_at else None,
                }
            }
        )
        
        return message
        
    except Message.DoesNotExist:
        raise ValueError(f"Message with id {message_id} does not exist")

def delete_message(message_id, user):
    """
    Удалить сообщение (мягкое удаление)
    """
    try:
        message = Message.objects.get(id=message_id, is_deleted=False)
        
        # Проверяем права на удаление
        if message.sender != user:
            raise PermissionError("User can only delete their own messages")
        
        message.delete_message()
        
        # Уведомляем через WebSocket
        channel_layer = get_channel_layer()
        room_name = f"chat_{message.chat.id}"
        
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'message_deleted',
                'message_id': message.id
            }
        )
        
        return message
        
    except Message.DoesNotExist:
        raise ValueError(f"Message with id {message_id} does not exist")

def add_user_to_chat(chat_id, user):
    """
    Добавить пользователя в чат
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        
        # Проверяем, не является ли чат приватным
        if chat.type == 'private':
            raise ValueError("Cannot add users to private chats")
        
        # Проверяем, не является ли пользователь уже участником
        if user in chat.participants.all():
            return chat
        
        ChatUser.objects.create(chat=chat, user=user)
        
        return chat
        
    except Chat.DoesNotExist:
        raise ValueError(f"Chat with id {chat_id} does not exist")

def remove_user_from_chat(chat_id, user):
    """
    Удалить пользователя из чата
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        
        # Проверяем, не является ли чат приватным
        if chat.type == 'private':
            raise ValueError("Cannot remove users from private chats")
        
        ChatUser.objects.filter(chat=chat, user=user).delete()
        
        return chat
        
    except Chat.DoesNotExist:
        raise ValueError(f"Chat with id {chat_id} does not exist")

def get_chat_participants(chat_id):
    """
    Получить участников чата
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        return chat.participants.all()
    except Chat.DoesNotExist:
        raise ValueError(f"Chat with id {chat_id} does not exist")

def is_user_in_chat(chat_id, user):
    """
    Проверить, является ли пользователь участником чата
    """
    try:
        chat = Chat.objects.get(id=chat_id)
        return user in chat.participants.all()
    except Chat.DoesNotExist:
        return False 
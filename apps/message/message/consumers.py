import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import Chat, Message, ChatUser
from core.authentication.models import User
from .utils import get_or_create_private_chat, send_message_to_chat, edit_message, delete_message

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Подключение к WebSocket с авторизацией"""
        self.user = None
        self.chat_id = None
        self.room_name = None
        
        # Получаем параметры из URL
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_name = f"chat_{self.chat_id}"
        
        # Проверяем авторизацию
        if not await self.authenticate_user():
            await self.close(code=401)  # Unauthorized
            return
        
        # Проверяем доступ к чату
        if not await self.can_access_chat():
            await self.close(code=403)  # Forbidden
            return
        
        # Присоединяемся к комнате
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Отправляем подтверждение подключения
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Successfully connected to chat',
            'chat_id': self.chat_id,
            'user_id': self.user.id,
            'username': self.user.username
        }))
        
        logger.info(f"User {self.user.id} connected to chat {self.chat_id}")

    async def disconnect(self, close_code):
        """Отключение от WebSocket"""
        if self.room_name:
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )
        
        if self.user:
            logger.info(f"User {self.user.id} disconnected from chat {self.chat_id}")

    async def receive(self, text_data):
        """Получение сообщения от клиента"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'edit_message':
                await self.handle_edit_message(data)
            elif message_type == 'delete_message':
                await self.handle_delete_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_messages':
                await self.handle_read_messages(data)
            elif message_type == 'get_messages':
                await self.handle_get_messages(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))

    async def handle_message(self, data):
        """Обработка нового сообщения"""
        text = data.get('text', '').strip()
        if not text:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message text cannot be empty'
            }))
            return
        
        try:
            # Сохраняем сообщение в базу данных
            message = await self.save_message(text)
            
            # Отправляем сообщение всем участникам чата
            await self.channel_layer.group_send(
                self.room_name,
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
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error sending message: {str(e)}'
            }))

    async def handle_edit_message(self, data):
        """Обработка редактирования сообщения"""
        message_id = data.get('message_id')
        new_text = data.get('text', '').strip()
        
        if not message_id or not new_text:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message ID and text are required'
            }))
            return
        
        try:
            # Редактируем сообщение
            message = await self.edit_message(message_id, new_text)
            
            # Отправляем обновленное сообщение всем участникам
            await self.channel_layer.group_send(
                self.room_name,
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
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error editing message: {str(e)}'
            }))

    async def handle_delete_message(self, data):
        """Обработка удаления сообщения"""
        message_id = data.get('message_id')
        
        if not message_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message ID is required'
            }))
            return
        
        try:
            # Удаляем сообщение
            await self.delete_message(message_id)
            
            # Отправляем уведомление об удалении всем участникам
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error deleting message: {str(e)}'
            }))

    async def handle_get_messages(self, data):
        """Обработка запроса сообщений с пагинацией"""
        page = data.get('page', 1)
        page_size = data.get('page_size', 50)
        
        try:
            messages = await self.get_messages_paginated(page, page_size)
            
            await self.send(text_data=json.dumps({
                'type': 'messages_list',
                'messages': messages,
                'page': page,
                'page_size': page_size
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error getting messages: {str(e)}'
            }))

    async def handle_typing(self, data):
        """Обработка индикатора печати"""
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing
            }
        )

    async def handle_read_messages(self, data):
        """Обработка отметки сообщений как прочитанных"""
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'messages_read',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )

    # WebSocket event handlers
    async def chat_message(self, event):
        """Отправка сообщения клиенту"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': event['message']
        }))

    async def message_edited(self, event):
        """Отправка уведомления об редактировании сообщения"""
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'data': event['message']
        }))

    async def message_deleted(self, event):
        """Отправка уведомления об удалении сообщения"""
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id']
        }))

    async def user_typing(self, event):
        """Отправка индикатора печати"""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))

    async def messages_read(self, event):
        """Отправка уведомления о прочтении сообщений"""
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'user_id': event['user_id'],
            'username': event['username']
        }))

    # Database operations
    @database_sync_to_async
    def authenticate_user(self):
        """Аутентификация пользователя через JWT токен"""
        try:
            # Получаем токен из заголовков или query параметров
            headers = dict(self.scope['headers'])
            auth_header = headers.get(b'authorization', b'').decode('utf-8')
            
            if not auth_header.startswith('Bearer '):
                return False
            
            token = auth_header.split(' ')[1]
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            
            self.user = User.objects.get(id=user_id)
            return True
            
        except (InvalidToken, TokenError, User.DoesNotExist, KeyError, IndexError):
            return False

    @database_sync_to_async
    def can_access_chat(self):
        """Проверка доступа пользователя к чату"""
        try:
            chat = Chat.objects.get(id=self.chat_id)
            return chat.participants.filter(id=self.user.id).exists()
        except Chat.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, text):
        """Сохранение сообщения в базу данных"""
        chat = Chat.objects.get(id=self.chat_id)
        message = Message.objects.create(
            chat=chat,
            sender=self.user,
            text=text
        )
        return message

    @database_sync_to_async
    def edit_message(self, message_id, new_text):
        """Редактирование сообщения"""
        return edit_message(message_id, self.user, new_text)

    @database_sync_to_async
    def delete_message(self, message_id):
        """Удаление сообщения"""
        return delete_message(message_id, self.user)

    @database_sync_to_async
    def get_messages_paginated(self, page, page_size):
        """Получение сообщений с пагинацией"""
        from .utils import get_chat_messages
        messages = get_chat_messages(self.chat_id, self.user, page, page_size)
        
        return [
            {
                'id': msg.id,
                'text': msg.text,
                'sender': {
                    'id': msg.sender.id,
                    'username': msg.sender.username,
                    'first_name': msg.sender.first_name,
                    'last_name': msg.sender.last_name,
                },
                'timestamp': msg.timestamp.isoformat(),
                'is_edited': msg.is_edited,
                'is_deleted': msg.is_deleted,
                'edited_at': msg.edited_at.isoformat() if msg.edited_at else None,
            }
            for msg in messages
        ] 
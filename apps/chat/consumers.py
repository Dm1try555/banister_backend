import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Авторизация через JWT
        self.user = await self.get_user_from_token()
        
        if self.user is None or isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Проверяем доступ к комнате
        has_access = await self.check_room_access()
        if not has_access:
            await self.close()
            return
        
        # Присоединяемся к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Покидаем группу комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'send_message':
                content = text_data_json.get('content', '')
                if content.strip():
                    # Сохраняем сообщение в БД
                    message = await self.save_message(content)
                    
                    # Отправляем всем в группе
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': {
                                'id': message.id,
                                'content': message.content,
                                'sender': {
                                    'id': message.sender.id,
                                    'username': message.sender.username
                                },
                                'created_at': message.created_at.isoformat()
                            }
                        }
                    )
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        # Отправляем сообщение в WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))
    
    @database_sync_to_async
    def get_user_from_token(self):
        try:
            # Получаем токен из query параметров
            query_string = self.scope.get('query_string', b'').decode()
            token = None
            
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=')[1]
                    break
            
            if not token:
                return None
            
            # Проверяем токен
            UntypedToken(token)
            
            # Получаем пользователя из токена
            from rest_framework_simplejwt.authentication import JWTAuthentication
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user = jwt_auth.get_user(validated_token)
            
            return user
            
        except (InvalidToken, TokenError, Exception):
            return None
    
    @database_sync_to_async
    def check_room_access(self):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            return room.participants.filter(id=self.user.id).exists()
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content):
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            room=room,
            sender=self.user,
            content=content
        )
        return message
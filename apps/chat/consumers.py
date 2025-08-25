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
    def connect(self):
        """Handle WebSocket connection"""
        # Authorization via JWT
        token = self.scope['url_route']['kwargs'].get('token')
        if not token:
            self.close()
            return
        
        # Check room access
        room_id = self.scope['url_route']['kwargs'].get('room_id')
        if not room_id:
            self.close()
            return
        
        # Join room group
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        async_to_sync(get_channel_layer().group_add)(
            f"chat_{room_id}",
            self.channel_name
        )
        
        self.accept()
    
    def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        room_id = self.scope['url_route']['kwargs'].get('room_id')
        if room_id:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            async_to_sync(get_channel_layer().group_discard)(
                f"chat_{room_id}",
                self.channel_name
            )
    
    def receive(self, text_data):
        """Handle incoming WebSocket message"""
        data = json.loads(text_data)
        message = data.get('message', '')
        room_id = data.get('room_id')
        
        # Save message to database
        if room_id and message:
            # Send to all in group
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            async_to_sync(get_channel_layer().group_send)(
                f"chat_{room_id}",
                {
                    'type': 'chat_message',
                    'message': message,
                    'room_id': room_id
                }
            )
    
    def chat_message(self, event):
        """Send message to WebSocket"""
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': event['message'],
            'room_id': event['room_id']
        }))
    
    @database_sync_to_async
    def get_user_from_token(self):
        try:
            # Get token from query parameters
            query_string = self.scope.get('query_string', b'').decode()
            token = None
            
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=')[1]
                    break
            
            if not token:
                return None
            
            # Check token
            UntypedToken(token)
            
            # Get user from token
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
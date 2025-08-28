import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection"""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Get user from token
        self.user = await self.get_user_from_token()
        if not self.user:
            await self.close()
            return
        
        # Check room access
        has_access = await self.check_room_access()
        if not has_access:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send recent messages
        await self.send_recent_messages()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_new_message(data)
            elif message_type == 'update_message':
                await self.handle_update_message(data)
            elif message_type == 'delete_message':
                await self.handle_delete_message(data)
            elif message_type == 'get_messages':
                await self.handle_get_messages(data)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def handle_new_message(self, data):
        """Handle new message"""
        content = data.get('content', '').strip()
        if not content:
            return
        
        # Save message to database
        message = await self.save_message(content)
        if message:
            # Send to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'sender': message.sender.username,
                        'sender_id': message.sender.id,
                        'created_at': message.created_at.isoformat(),
                        'updated_at': message.updated_at.isoformat(),
                        'is_deleted': message.is_deleted
                    }
                }
            )
    
    async def handle_update_message(self, data):
        """Handle message update"""
        message_id = data.get('message_id')
        new_content = data.get('content', '').strip()
        
        if not message_id or not new_content:
            return
        
        # Update message
        success = await self.update_message(message_id, new_content)
        if success:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_updated',
                    'message_id': message_id,
                    'content': new_content,
                    'updated_at': success.updated_at.isoformat()
                }
            )
    
    async def handle_delete_message(self, data):
        """Handle message deletion"""
        message_id = data.get('message_id')
        if not message_id:
            return
        
        # Delete message
        success = await self.delete_message(message_id)
        if success:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id
                }
            )
    
    async def handle_get_messages(self, data):
        """Handle get messages request"""
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        
        messages = await self.get_messages_paginated(page, page_size)
        await self.send(text_data=json.dumps({
            'type': 'messages_history',
            'messages': messages,
            'page': page,
            'page_size': page_size
        }))
    
    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
    
    async def message_updated(self, event):
        """Send message update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_updated',
            'message_id': event['message_id'],
            'content': event['content'],
            'updated_at': event['updated_at']
        }))
    
    async def message_deleted(self, event):
        """Send message deletion to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id']
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
            
        except (InvalidToken, TokenError, Exception) as e:
            logger.error(f"Token validation error: {e}")
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
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            message = Message.objects.create(
                room=room,
                sender=self.user,
                content=content
            )
            return message
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return None
    
    @database_sync_to_async
    def update_message(self, message_id, new_content):
        try:
            message = Message.objects.get(
                id=message_id,
                sender=self.user,
                room_id=self.room_id,
                is_deleted=False
            )
            message.content = new_content
            message.save()
            return message
        except Message.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error updating message: {e}")
            return None
    
    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            message = Message.objects.get(
                id=message_id,
                sender=self.user,
                room_id=self.room_id,
                is_deleted=False
            )
            message.is_deleted = True
            message.save()
            return True
        except Message.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            return False
    
    @database_sync_to_async
    def get_messages_paginated(self, page, page_size):
        try:
            from django.core.paginator import Paginator
            
            messages = Message.objects.filter(
                room_id=self.room_id,
                is_deleted=False
            ).select_related('sender').order_by('-created_at')
            
            paginator = Paginator(messages, page_size)
            page_obj = paginator.get_page(page)
            
            return [
                {
                    'id': msg.id,
                    'content': msg.content,
                    'sender': msg.sender.username,
                    'sender_id': msg.sender.id,
                    'created_at': msg.created_at.isoformat(),
                    'updated_at': msg.updated_at.isoformat(),
                    'is_deleted': msg.is_deleted
                }
                for msg in page_obj
            ]
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    @database_sync_to_async
    def get_recent_messages(self, limit=20):
        try:
            messages = Message.objects.filter(
                room_id=self.room_id,
                is_deleted=False
            ).select_related('sender').order_by('-created_at')[:limit]
            
            return [
                {
                    'id': msg.id,
                    'content': msg.content,
                    'sender': msg.sender.username,
                    'sender_id': msg.sender.id,
                    'created_at': msg.created_at.isoformat(),
                    'updated_at': msg.updated_at.isoformat(),
                    'is_deleted': msg.is_deleted
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    async def send_recent_messages(self):
        """Send recent messages to the user"""
        messages = await self.get_recent_messages()
        await self.send(text_data=json.dumps({
            'type': 'recent_messages',
            'messages': messages
        }))
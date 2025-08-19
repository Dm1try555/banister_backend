import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Chat, Message
from apps.authentication.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'
        
        # Check if user is authenticated
        if self.scope['user'] == AnonymousUser():
            await self.close()
            return
        
        # Check if user has access to this chat
        if not await self.user_has_chat_access():
            await self.close()
            return
        
        # Join chat group
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave chat group
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'send_message':
            await self.send_message(data)
        elif action == 'edit_message':
            await self.edit_message(data)
        elif action == 'delete_message':
            await self.delete_message(data)
    
    async def send_message(self, data):
        content = data.get('content', '')
        if not content.strip():
            return
        
        # Save message to database
        message = await self.create_message(content)
        
        # Send message to chat group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'created_at': message.created_at.isoformat(),
                    'is_edited': message.is_edited
                }
            }
        )
    
    async def edit_message(self, data):
        message_id = data.get('message_id')
        new_content = data.get('content', '')
        
        if not new_content.strip():
            return
        
        # Update message in database
        message = await self.update_message(message_id, new_content)
        if not message:
            return
        
        # Send updated message to chat group
        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'message_edited',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'created_at': message.created_at.isoformat(),
                    'updated_at': message.updated_at.isoformat(),
                    'is_edited': message.is_edited
                }
            }
        )
    
    async def delete_message(self, data):
        message_id = data.get('message_id')
        
        # Delete message from database
        if await self.remove_message(message_id):
            # Send delete notification to chat group
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id
                }
            )
    
    # WebSocket message handlers
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'data': event['message']
        }))
    
    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_edited',
            'data': event['message']
        }))
    
    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id']
        }))
    
    # Database operations
    @database_sync_to_async
    def user_has_chat_access(self):
        try:
            chat = Chat.objects.get(id=self.chat_id)
            return chat.participants.filter(id=self.scope['user'].id).exists()
        except Chat.DoesNotExist:
            return False
    
    @database_sync_to_async
    def create_message(self, content):
        chat = Chat.objects.get(id=self.chat_id)
        return Message.objects.create(
            chat=chat,
            sender=self.scope['user'],
            content=content
        )
    
    @database_sync_to_async
    def update_message(self, message_id, content):
        try:
            message = Message.objects.get(
                id=message_id,
                sender=self.scope['user'],
                chat_id=self.chat_id
            )
            message.content = content
            message.is_edited = True
            message.save()
            return message
        except Message.DoesNotExist:
            return None
    
    @database_sync_to_async
    def remove_message(self, message_id):
        try:
            message = Message.objects.get(
                id=message_id,
                sender=self.scope['user'],
                chat_id=self.chat_id
            )
            message.delete()
            return True
        except Message.DoesNotExist:
            return False
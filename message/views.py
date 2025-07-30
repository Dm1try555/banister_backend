from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import PermissionError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class ChatListView(BaseAPIView, generics.ListAPIView):
    """User chat list"""
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)

    @swagger_auto_schema(
        operation_description="Get list of all user chats",
        responses={
            200: openapi.Response('Chat list', ChatSerializer(many=True)),
        },
        tags=['Chats and Messages']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Chat list retrieved successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='CHAT_LIST_ERROR',
                error_message=f'Error retrieving chat list: {str(e)}',
                status_code=500
            )

class ChatDetailView(BaseAPIView, generics.RetrieveAPIView):
    """Detailed chat information"""
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user not in obj.participants.all():
            raise PermissionError('No permissions to view this chat')
        return obj

    @swagger_auto_schema(
        operation_description="Get detailed chat information by ID",
        responses={
            200: openapi.Response('Chat information', ChatSerializer),
            404: 'Chat not found',
        },
        tags=['Chats and Messages']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Chat information retrieved successfully'
            )
            
        except Chat.DoesNotExist:
            return self.error_response(
                error_number='CHAT_NOT_FOUND',
                error_message='Chat not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='CHAT_RETRIEVE_ERROR',
                error_message=f'Error retrieving chat information: {str(e)}',
                status_code=500
            )

class MessageCreateView(BaseAPIView, generics.CreateAPIView):
    """Create new message"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @swagger_auto_schema(
        operation_description="Send message to chat",
        request_body=MessageSerializer,
        responses={
            201: openapi.Response('Message sent', MessageSerializer),
            400: 'Validation error',
            403: 'No permissions',
            404: 'Chat not found',
        },
        tags=['Chats and Messages']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Check chat existence
            chat_id = serializer.validated_data.get('chat')
            try:
                chat = Chat.objects.get(id=chat_id)
                if self.request.user not in chat.participants.all():
                    return self.error_response(
                        error_number='PERMISSION_ERROR',
                        error_message='No permissions to send messages to this chat',
                        status_code=403
                    )
            except Chat.DoesNotExist:
                return self.error_response(
                    error_number='CHAT_NOT_FOUND',
                    error_message='Chat not found',
                    status_code=404
                )
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Message sent successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_CREATE_ERROR',
                error_message=f'Error sending message: {str(e)}',
                status_code=500
            )

class MessageDetailView(BaseAPIView, generics.RetrieveAPIView):
    """Detailed message information"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user not in obj.chat.participants.all():
            raise PermissionError('No permissions to view this message')
        return obj

    @swagger_auto_schema(
        operation_description="Get detailed message information by ID",
        responses={
            200: openapi.Response('Message information', MessageSerializer),
            404: 'Message not found',
        },
        tags=['Chats and Messages']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Message retrieved successfully'
            )
            
        except Message.DoesNotExist:
            return self.error_response(
                error_number='MESSAGE_NOT_FOUND',
                error_message='Message not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_RETRIEVE_ERROR',
                error_message=f'Error retrieving message: {str(e)}',
                status_code=500
            )

class MessageListCreateView(BaseAPIView, generics.ListCreateAPIView):
    """List of messages and creation of new ones"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # You can filter messages by user participation in the chat if needed
        return Message.objects.filter(chat__participants=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        chat_id = serializer.validated_data.get('chat')
        chat = Chat.objects.get(id=chat_id)
        if self.request.user not in chat.participants.all():
            raise PermissionError('No permissions to send messages to this chat')
        serializer.save(sender=self.request.user)

    @swagger_auto_schema(
        operation_description="Get list of all user chats",
        responses={
            200: openapi.Response('Chat list', ChatSerializer(many=True)),
        },
        tags=['Chats and Messages']
    )
    def list(self, request, *args, **kwargs):
        try:
            # Return user chat list (like ChatListView)
            queryset = Chat.objects.filter(participants=self.request.user)
            serializer = ChatSerializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message='Chat list retrieved successfully'
            )
        except Exception as e:
            return self.error_response(
                error_number='CHAT_LIST_ERROR',
                error_message=f'Error retrieving chat list: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Send message to chat",
        request_body=MessageSerializer,
        responses={
            201: openapi.Response('Message sent', MessageSerializer),
            400: 'Validation error',
            403: 'No permissions',
            404: 'Chat not found',
        },
        tags=['Chats and Messages']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            # Check chat existence
            chat_id = serializer.validated_data.get('chat')
            try:
                chat = Chat.objects.get(id=chat_id)
                if self.request.user not in chat.participants.all():
                    return self.error_response(
                        error_number='PERMISSION_ERROR',
                        error_message='No permissions to send messages to this chat',
                        status_code=403
                    )
            except Chat.DoesNotExist:
                return self.error_response(
                    error_number='CHAT_NOT_FOUND',
                    error_message='Chat not found',
                    status_code=404
                )
            serializer.save(sender=self.request.user)
            return self.success_response(
                data=serializer.data,
                message='Message sent successfully'
            )
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_CREATE_ERROR',
                error_message=f'Error sending message: {str(e)}',
                status_code=500
            )
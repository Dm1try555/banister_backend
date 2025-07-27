from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import PermissionError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class ChatListView(BaseAPIView, generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить список всех чатов пользователя",
        responses={
            200: openapi.Response('Список чатов', ChatSerializer(many=True)),
        },
        tags=['Чаты и сообщения']
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Список чатов получен успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='CHAT_LIST_ERROR',
                error_message=f'Ошибка получения списка чатов: {str(e)}',
                status_code=500
            )

class ChatDetailView(BaseAPIView, generics.RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user not in obj.participants.all():
            raise PermissionError('Нет прав для просмотра этого чата')
        return obj

    @swagger_auto_schema(
        operation_description="Получить подробную информацию о чате по ID",
        responses={
            200: openapi.Response('Информация о чате', ChatSerializer),
            404: 'Чат не найден',
        },
        tags=['Чаты и сообщения']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Информация о чате получена успешно'
            )
            
        except Chat.DoesNotExist:
            return self.error_response(
                error_number='CHAT_NOT_FOUND',
                error_message='Чат не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='CHAT_RETRIEVE_ERROR',
                error_message=f'Ошибка получения информации о чате: {str(e)}',
                status_code=500
            )

class MessageCreateView(BaseAPIView, generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @swagger_auto_schema(
        operation_description="Отправить сообщение в чат",
        request_body=MessageSerializer,
        responses={
            201: openapi.Response('Сообщение отправлено', MessageSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
            404: 'Чат не найден',
        },
        tags=['Чаты и сообщения']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Проверка существования чата
            chat_id = serializer.validated_data.get('chat')
            try:
                chat = Chat.objects.get(id=chat_id)
                if self.request.user not in chat.participants.all():
                    return self.error_response(
                        error_number='PERMISSION_ERROR',
                        error_message='Нет прав для отправки сообщений в этот чат',
                        status_code=403
                    )
            except Chat.DoesNotExist:
                return self.error_response(
                    error_number='CHAT_NOT_FOUND',
                    error_message='Чат не найден',
                    status_code=404
                )
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Сообщение отправлено успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_CREATE_ERROR',
                error_message=f'Ошибка отправки сообщения: {str(e)}',
                status_code=500
            )

class MessageDetailView(BaseAPIView, generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user not in obj.chat.participants.all():
            raise PermissionError('Нет прав для просмотра этого сообщения')
        return obj

    @swagger_auto_schema(
        operation_description="Получить подробную информацию о сообщении по ID",
        responses={
            200: openapi.Response('Информация о сообщении', MessageSerializer),
            404: 'Сообщение не найдено',
        },
        tags=['Чаты и сообщения']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Сообщение получено успешно'
            )
            
        except Message.DoesNotExist:
            return self.error_response(
                error_number='MESSAGE_NOT_FOUND',
                error_message='Сообщение не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_RETRIEVE_ERROR',
                error_message=f'Ошибка получения сообщения: {str(e)}',
                status_code=500
            )

class MessageListCreateView(BaseAPIView, generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Можно фильтровать сообщения по участию пользователя в чате, если нужно
        return Message.objects.filter(chat__participants=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        chat_id = serializer.validated_data.get('chat')
        chat = Chat.objects.get(id=chat_id)
        if self.request.user not in chat.participants.all():
            raise PermissionError('Нет прав для отправки сообщений в этот чат')
        serializer.save(sender=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить список всех чатов пользователя",
        responses={
            200: openapi.Response('Список чатов', ChatSerializer(many=True)),
        },
        tags=['Чаты и сообщения']
    )
    def list(self, request, *args, **kwargs):
        try:
            # Возвращаем список чатов пользователя (как ChatListView)
            queryset = Chat.objects.filter(participants=self.request.user)
            serializer = ChatSerializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message='Список чатов получен успешно'
            )
        except Exception as e:
            return self.error_response(
                error_number='CHAT_LIST_ERROR',
                error_message=f'Ошибка получения списка чатов: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Отправить сообщение в чат",
        request_body=MessageSerializer,
        responses={
            201: openapi.Response('Сообщение отправлено', MessageSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
            404: 'Чат не найден',
        },
        tags=['Чаты и сообщения']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            # Проверка существования чата
            chat_id = serializer.validated_data.get('chat')
            try:
                chat = Chat.objects.get(id=chat_id)
                if self.request.user not in chat.participants.all():
                    return self.error_response(
                        error_number='PERMISSION_ERROR',
                        error_message='Нет прав для отправки сообщений в этот чат',
                        status_code=403
                    )
            except Chat.DoesNotExist:
                return self.error_response(
                    error_number='CHAT_NOT_FOUND',
                    error_message='Чат не найден',
                    status_code=404
                )
            serializer.save(sender=self.request.user)
            return self.success_response(
                data=serializer.data,
                message='Сообщение отправлено успешно'
            )
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_CREATE_ERROR',
                error_message=f'Ошибка отправки сообщения: {str(e)}',
                status_code=500
            )
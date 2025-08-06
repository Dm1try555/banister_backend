from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.utils import timezone
from .models import Chat, Message, ChatUser
from .serializers import (
    ChatSerializer, MessageSerializer, MessageCreateSerializer, 
    MessageUpdateSerializer, ChatCreateSerializer, PrivateChatCreateSerializer
)
from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import get_or_create_private_chat, send_message_to_chat, edit_message, delete_message, get_chat_messages

class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class ChatListView(BaseAPIView, generics.ListCreateAPIView):
    """Список чатов пользователя и создание нового чата"""
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post']
    
    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            chat_type = self.request.data.get('type', 'private')
            if chat_type == 'private':
                return PrivateChatCreateSerializer
            return ChatCreateSerializer
        return ChatSerializer
    
    @transaction.atomic
    def perform_create(self, serializer):
        chat = serializer.save()
        # Добавляем текущего пользователя как участника
        ChatUser.objects.create(chat=chat, user=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить список всех чатов пользователя",
        responses={
            200: openapi.Response('Список чатов', ChatSerializer(many=True)),
        },
        tags=['Chats and Messages']
    )
    def get(self, request, *args, **kwargs):
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

    @swagger_auto_schema(
        operation_description="Создать новый чат (приватный или групповой)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'type': openapi.Schema(type=openapi.TYPE_STRING, enum=['private', 'group'], description='Тип чата'),
                'participant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID участника для приватного чата'),
                'participants': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER), description='Список ID участников для группового чата'),
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Название группового чата'),
            }
        ),
        responses={
            201: openapi.Response('Чат создан', ChatSerializer),
            400: 'Ошибка валидации',
        },
        tags=['Chats and Messages']
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            chat_type = request.data.get('type', 'private')
            
            if chat_type == 'private':
                # Создание приватного чата
                participant_id = request.data.get('participant_id')
                if not participant_id:
                    return self.error_response(
                        error_number='MISSING_PARTICIPANT',
                        error_message='participant_id обязателен для приватного чата',
                        status_code=400
                    )
                
                try:
                    from core.authentication.models import User
                    participant = User.objects.get(id=participant_id)
                    chat = get_or_create_private_chat(request.user, participant)
                except User.DoesNotExist:
                    return self.error_response(
                        error_number='USER_NOT_FOUND',
                        error_message='Участник не найден',
                        status_code=404
                    )
            else:
                # Создание группового чата
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                chat = serializer.save()
            
            # Возвращаем созданный чат
            chat_serializer = ChatSerializer(chat, context={'request': request})
            
            return self.success_response(
                data=chat_serializer.data,
                message='Чат создан успешно',
                status_code=201
            )
            
        except Exception as e:
            return self.error_response(
                error_number='CHAT_CREATE_ERROR',
                error_message=f'Ошибка создания чата: {str(e)}',
                status_code=400
            )

class ChatDetailView(BaseAPIView, generics.RetrieveAPIView):
    """Детальная информация о чате"""
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_object(self):
        obj = super().get_object()
        if self.request.user not in obj.participants.all():
            raise CustomPermissionError('Нет прав для просмотра этого чата')
        return obj

    @swagger_auto_schema(
        operation_description="Получить детальную информацию о чате",
        responses={
            200: openapi.Response('Информация о чате', ChatSerializer),
            404: 'Чат не найден',
        },
        tags=['Chats and Messages']
    )
    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, context={'request': request})
            
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

class MessageListView(BaseAPIView, generics.ListAPIView):
    """Список сообщений в чате с пагинацией"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination
    http_method_names = ['get']

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        try:
            chat = Chat.objects.get(id=chat_id)
            if self.request.user not in chat.participants.all():
                raise CustomPermissionError('Нет прав для просмотра сообщений в этом чате')
            return Message.objects.filter(chat=chat, is_deleted=False).order_by('-timestamp')
        except Chat.DoesNotExist:
            return Message.objects.none()

    @swagger_auto_schema(
        operation_description="Получить список сообщений в чате с пагинацией",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Номер страницы", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Размер страницы", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response('Список сообщений', MessageSerializer(many=True)),
            404: 'Чат не найден',
        },
        tags=['Chats and Messages']
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            if not queryset.exists():
                return self.error_response(
                    error_number='CHAT_NOT_FOUND',
                    error_message='Чат не найден или у вас нет прав доступа',
                    status_code=404
                )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return self.success_response(
                data=serializer.data,
                message='Список сообщений получен успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_LIST_ERROR',
                error_message=f'Ошибка получения списка сообщений: {str(e)}',
                status_code=500
            )

class MessageCreateView(BaseAPIView, generics.CreateAPIView):
    """Создание нового сообщения"""
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']
    
    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @swagger_auto_schema(
        operation_description="Отправить сообщение в чат",
        request_body=MessageCreateSerializer,
        responses={
            201: openapi.Response('Сообщение отправлено', MessageSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
            404: 'Чат не найден',
        },
        tags=['Chats and Messages']
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Проверяем доступ к чату
            chat_id = serializer.validated_data['chat'].id
            chat = Chat.objects.get(id=chat_id)
            if request.user not in chat.participants.all():
                return self.error_response(
                    error_number='NO_CHAT_ACCESS',
                    error_message='Нет прав для отправки сообщений в этот чат',
                    status_code=403
                )
            
            message = serializer.save(sender=request.user)
            
            # Отправляем сообщение через WebSocket
            try:
                send_message_to_chat(chat_id, request.user, message.text)
            except Exception as e:
                # Логируем ошибку WebSocket, но не прерываем создание сообщения
                print(f"WebSocket error: {e}")
            
            # Возвращаем созданное сообщение
            message_serializer = MessageSerializer(message)
            
            return self.success_response(
                data=message_serializer.data,
                message='Сообщение отправлено успешно',
                status_code=201
            )
            
        except Chat.DoesNotExist:
            return self.error_response(
                error_number='CHAT_NOT_FOUND',
                error_message='Чат не найден',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_CREATE_ERROR',
                error_message=f'Ошибка отправки сообщения: {str(e)}',
                status_code=400
            )

class MessageDetailView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    """Детальная информация о сообщении, редактирование и удаление"""
    queryset = Message.objects.filter(is_deleted=False)
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'delete']

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MessageUpdateSerializer
        return MessageSerializer

    def get_object(self):
        obj = super().get_object()
        # Проверяем права на просмотр/редактирование сообщения
        if self.request.user != obj.sender:
            raise CustomPermissionError('Нет прав для работы с этим сообщением')
        return obj

    @swagger_auto_schema(
        operation_description="Получить информацию о сообщении",
        responses={
            200: openapi.Response('Информация о сообщении', MessageSerializer),
            404: 'Сообщение не найдено',
        },
        tags=['Chats and Messages']
    )
    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Информация о сообщении получена успешно'
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
                error_message=f'Ошибка получения информации о сообщении: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Редактировать сообщение",
        request_body=MessageUpdateSerializer,
        responses={
            200: openapi.Response('Сообщение обновлено', MessageSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
            404: 'Сообщение не найдено',
        },
        tags=['Chats and Messages']
    )
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Обновляем сообщение
            instance.edit_message(serializer.validated_data['text'])
            
            # Возвращаем обновленное сообщение
            message_serializer = MessageSerializer(instance)
            
            return self.success_response(
                data=message_serializer.data,
                message='Сообщение обновлено успешно'
            )
            
        except Message.DoesNotExist:
            return self.error_response(
                error_number='MESSAGE_NOT_FOUND',
                error_message='Сообщение не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_UPDATE_ERROR',
                error_message=f'Ошибка обновления сообщения: {str(e)}',
                status_code=400
            )

    @swagger_auto_schema(
        operation_description="Удалить сообщение",
        responses={
            200: 'Сообщение удалено',
            403: 'Нет прав',
            404: 'Сообщение не найдено',
        },
        tags=['Chats and Messages']
    )
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete_message()
            
            return self.success_response(
                data=None,
                message='Сообщение удалено успешно'
            )
            
        except Message.DoesNotExist:
            return self.error_response(
                error_number='MESSAGE_NOT_FOUND',
                error_message='Сообщение не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='MESSAGE_DELETE_ERROR',
                error_message=f'Ошибка удаления сообщения: {str(e)}',
                status_code=500
            )
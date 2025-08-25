from core.base.common_imports import *
from .models import ChatRoom, Message
from .serializers import (
    ChatRoomSerializer, ChatRoomCreateSerializer, ChatRoomUpdateSerializer,
    MessageSerializer, MessageCreateSerializer, MessageUpdateSerializer
)
from .permissions import ChatPermissions


class ChatRoomListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, ChatPermissions):
    permission_classes = [IsAuthenticated]
    queryset = ChatRoom.objects.all()

    def get_serializer_class(self):
        return ChatRoomCreateSerializer if self.request.method == 'POST' else ChatRoomSerializer

    @swagger_list_create(
        description="Create new chat room",
        response_schema=CHAT_ROOM_RESPONSE_SCHEMA,
        tags=["Chat"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        chat_room = serializer.save()
        chat_room.participants.add(self.request.user)


class ChatRoomDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin, ChatPermissions):
    permission_classes = [IsAuthenticated]
    queryset = ChatRoom.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ChatRoomUpdateSerializer
        return ChatRoomSerializer

    @swagger_retrieve_update_destroy(
        description="Retrieve, update or delete chat room",
        response_schema=CHAT_ROOM_RESPONSE_SCHEMA,
        tags=["Chat"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Update chat room",
        response_schema=CHAT_ROOM_RESPONSE_SCHEMA,
        tags=["Chat"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Partially update chat room",
        response_schema=CHAT_ROOM_RESPONSE_SCHEMA,
        tags=["Chat"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete chat room",
        response_schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        tags=["Chat"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class MessageListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, ChatPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def get_serializer_class(self):
        return MessageCreateSerializer if self.request.method == 'POST' else MessageSerializer

    @swagger_list_create(
        description="Create new message",
        response_schema=MESSAGE_RESPONSE_SCHEMA,
        tags=["Chat Messages"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        room_id = self.request.query_params.get('room')
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        return queryset.filter(is_deleted=False).order_by('-created_at')


class MessageDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin, ChatPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MessageUpdateSerializer
        return MessageSerializer

    @swagger_retrieve_update_destroy(
        description="Retrieve, update or delete message",
        response_schema=MESSAGE_RESPONSE_SCHEMA,
        tags=["Chat Messages"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Update message",
        response_schema=MESSAGE_RESPONSE_SCHEMA,
        tags=["Chat Messages"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Partially update message",
        response_schema=MESSAGE_RESPONSE_SCHEMA,
        tags=["Chat Messages"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete message",
        response_schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        tags=["Chat Messages"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
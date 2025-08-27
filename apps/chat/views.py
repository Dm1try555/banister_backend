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
    @transaction.atomic
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
    @transaction.atomic
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


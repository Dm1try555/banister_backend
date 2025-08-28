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

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    @swagger_auto_schema(
        operation_description="Update message",
        request_body=MessageUpdateSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                    'sender': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_at': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            404: ERROR_404_SCHEMA
        }
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        message = self.get_object()
        # Check if user is the sender
        if message.sender != request.user:
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete message (soft delete)",
        responses={
            204: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            404: ERROR_404_SCHEMA
        }
    )
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        message = self.get_object()
        # Check if user is the sender
        if message.sender != request.user:
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        
        # Soft delete
        message.is_deleted = True
        message.save()
        
        return Response({
            'message': 'Message deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class MessageListByRoomView(SwaggerMixin, ListAPIView, RoleBasedQuerysetMixin, ChatPermissions):
    """Get messages for a specific room with pagination"""
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        return Message.objects.filter(
            room_id=room_id,
            is_deleted=False
        ).select_related('sender').order_by('-created_at')

    @swagger_auto_schema(
        operation_description="Get messages for a specific room",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'next': openapi.Schema(type=openapi.TYPE_STRING),
                    'previous': openapi.Schema(type=openapi.TYPE_STRING),
                    'results': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'content': openapi.Schema(type=openapi.TYPE_STRING),
                                'sender': openapi.Schema(type=openapi.TYPE_STRING),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    )
                }
            ),
            404: ERROR_404_SCHEMA
        }
    )
    def get(self, request, *args, **kwargs):
        # Check if user has access to the room
        room_id = self.kwargs.get('room_id')
        try:
            room = ChatRoom.objects.get(id=room_id)
            if not room.participants.filter(id=request.user.id).exists():
                raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        except ChatRoom.DoesNotExist:
            raise CustomValidationError(ErrorCode.USER_NOT_FOUND)
        
        return super().get(request, *args, **kwargs)


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        room = serializer.save()
        room.participants.add(request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        room_id = self.kwargs.get('room_id')
        if room_id:
            return Message.objects.filter(
                room_id=room_id,
                room__participants=self.request.user,
                is_deleted=False
            )
        return Message.objects.none()
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        room_id = self.kwargs.get('room_id')
        room = ChatRoom.objects.filter(
            id=room_id, 
            participants=request.user
        ).first()
        
        if not room:
            return Response(
                {'error': 'Room not found or access denied'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender=request.user, room=room)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        message = self.get_object()
        
        if message.sender != request.user:
            return Response(
                {'error': 'You can only edit your own messages'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        
        if message.sender != request.user:
            return Response(
                {'error': 'You can only delete your own messages'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.is_deleted = True
        message.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
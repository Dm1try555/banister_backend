from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Notification
from .serializers import NotificationSerializer
from core.firebase.service import firebase_service

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Notification.objects.filter(user=self.request.user)
        return Notification.objects.none()
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create notification and send via Firebase"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save to database
        notification = serializer.save()
        
        # Send via Firebase (if user has token)
        user_token = getattr(notification.user, 'firebase_token', None)
        if user_token:
            firebase_service.send_notification(
                user_token=user_token,
                title=f"New {notification.notification_type}",
                body=f"You have a new notification: {notification.notification_type}",
                data=notification.data
            )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all notifications marked as read'})
    
    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """Delete all notifications"""
        count = self.get_queryset().count()
        self.get_queryset().delete()
        return Response({'status': f'{count} notifications deleted'})
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        unread_notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)
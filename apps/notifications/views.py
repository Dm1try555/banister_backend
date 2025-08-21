from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Notification
from .serializers import NotificationSerializer
from core.firebase.service import firebase_service
from core.base.views import CustomerViewSet

class NotificationViewSet(CustomerViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        notification_data = super().create(request, *args, **kwargs).data
        
        user_token = getattr(request.user, 'firebase_token', None)
        if user_token:
            firebase_service.send_notification(
                user_token=user_token,
                title=f"New {notification_data['notification_type']}",
                body=f"You have a new notification: {notification_data['notification_type']}",
                data=notification_data['data']
            )
        
        return Response(notification_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'all notifications marked as read'})
    
    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        count = self.get_queryset().count()
        self.get_queryset().delete()
        return Response({'status': f'{count} notifications deleted'})
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        unread_notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)
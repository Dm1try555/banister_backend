from core.base.common_imports import *
from .models import Notification
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer, NotificationUpdateSerializer
)
from .permissions import NotificationPermissions
from core.notifications.service import notification_service


class NotificationListCreateView(OptimizedListCreateView, NotificationPermissions):
    queryset = Notification.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        return NotificationCreateSerializer if self.request.method == 'POST' else NotificationSerializer

    @swagger_list_create(
        description="Create new notification",
        response_schema=NOTIFICATION_RESPONSE_SCHEMA,
        tags=["Notifications"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationDetailView(OptimizedRetrieveUpdateDestroyView, NotificationPermissions):
    queryset = Notification.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NotificationUpdateSerializer
        return NotificationSerializer


class NotificationMarkAsReadView(BaseAPIView):
    """Mark notification as read"""
    
    @swagger_auto_schema(
        operation_description="Mark notification as read",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            404: ERROR_404_SCHEMA
        }
    )
    @transaction.atomic
    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(
                id=pk,
                user=request.user
            )
            notification.is_read = True
            notification.save()
            
            return self.get_success_response(message='Notification marked as read')
        except Notification.DoesNotExist:
            raise CustomValidationError(ErrorCode.USER_NOT_FOUND)


class NotificationDeleteAllView(BaseAPIView):
    """Delete all notifications for current user"""
    
    @swagger_auto_schema(
        operation_description="Delete all notifications for current user",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'deleted_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )
        }
    )
    @transaction.atomic
    def delete(self, request):
        deleted_count, _ = Notification.objects.filter(
            user=request.user
        ).delete()
        
        return self.get_success_response(
            data={'deleted_count': deleted_count},
            message='All notifications deleted'
        )


class NotificationMarkAllAsReadView(BaseAPIView):
    """Mark all notifications as read for current user"""
    
    @swagger_auto_schema(
        operation_description="Mark all notifications as read for current user",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'updated_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )
        }
    )
    @transaction.atomic
    def patch(self, request):
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        
        return self.get_success_response(
            data={'updated_count': updated_count},
            message='All notifications marked as read'
        )


class NotificationUnreadCountView(BaseAPIView):
    """Get unread notifications count for current user"""
    
    @swagger_auto_schema(
        operation_description="Get unread notifications count",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'unread_count': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            )
        }
    )
    def get(self, request):
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return self.get_success_response(data={'unread_count': unread_count})


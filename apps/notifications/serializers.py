from core.base.common_imports import *
from core.error_handling import ErrorCode
from .models import Notification


class BaseNotificationSerializer(OptimizedModelSerializer):
    """Базовый serializer для уведомлений"""
    
    class Meta:
        model = Notification
        abstract = True
    
    def validate_notification_type(self, value):
        """Валидация типа уведомления"""
        from core.notifications.service import NotificationService
        valid_types = list(NotificationService.NOTIFICATION_TYPES.values())
        if value not in valid_types:
            ErrorCode.INVALID_DATA.raise_error()
        return value

    def validate_data(self, value):
        """Валидация данных уведомления"""
        if not value or not isinstance(value, dict):
            ErrorCode.INVALID_DATA.raise_error()
        return value


class NotificationSerializer(BaseNotificationSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'data', 'is_read',
            'created_at'
        ]


class NotificationCreateSerializer(BaseNotificationSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'data', 'is_read', 'created_at']


class NotificationUpdateSerializer(BaseNotificationSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']
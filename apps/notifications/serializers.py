from core.base.common_imports import *
from core.error_handling import ErrorCode

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'data', 'is_read',
            'created_at'
        ]


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notification_type', 'data']

    def validate_notification_type(self, value):
        valid_types = ['booking_confirmed', 'booking_cancelled', 'payment_received', 'payment_failed', 'reminder']
        if value not in valid_types:
            ErrorCode.INVALID_DATA.raise_error()
        return value

    def validate_data(self, value):
        if not value or not isinstance(value, dict):
            ErrorCode.INVALID_DATA.raise_error()
        return value


class NotificationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']
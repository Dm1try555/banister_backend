from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения уведомлений"""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_email', 'notification_type', 'notification_type_display',
            'data', 'status', 'status_display', 'fcm_token', 'created_at', 'read_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'notification_type_display', 'status_display',
            'created_at', 'read_at'
        ]


class CreateNotificationSerializer(serializers.ModelSerializer):
    """Сериализатор для создания уведомлений"""
    
    class Meta:
        model = Notification
        fields = [
            'user', 'notification_type', 'data', 'fcm_token'
        ]
    
    def validate_notification_type(self, value):
        """Проверить тип уведомления"""
        valid_types = [choice[0] for choice in Notification.NOTIFICATION_TYPES]
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Неверный тип уведомления. Допустимые типы: {', '.join(valid_types)}"
            )
        return value


class NotificationStatusSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления статуса уведомления"""
    
    class Meta:
        model = Notification
        fields = ['status']
    
    def validate_status(self, value):
        """Проверить статус уведомления"""
        valid_statuses = [choice[0] for choice in Notification.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Неверный статус. Допустимые статусы: {', '.join(valid_statuses)}"
            )
        return value


class NotificationListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка уведомлений с пагинацией"""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display', 'data',
            'status', 'status_display', 'created_at', 'read_at'
        ] 
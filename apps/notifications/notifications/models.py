from django.db import models
from django.utils import timezone
from core.authentication.models import User


class Notification(models.Model):
    """Модель для хранения уведомлений"""
    
    NOTIFICATION_TYPES = (
        ('ClientSendBookingNotigicationToAdmin', 'Уведомление о бронировании от клиента к админу'),
        ('BookingConfirmed', 'Бронирование подтверждено'),
        ('BookingCancelled', 'Бронирование отменено'),
        ('PaymentReceived', 'Платеж получен'),
        ('PaymentFailed', 'Ошибка платежа'),
        ('ServiceUpdated', 'Услуга обновлена'),
        ('NewMessage', 'Новое сообщение'),
        ('SystemAlert', 'Системное уведомление'),
    )
    
    STATUS_CHOICES = (
        ('unread', 'Не прочитано'),
        ('read', 'Прочитано'),
        ('deleted', 'Удалено'),
    )
    
    # Основные поля
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=100, choices=NOTIFICATION_TYPES)
    data = models.JSONField(default=dict, blank=True, help_text="Дополнительные данные уведомления")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    
    # Firebase FCM token для отправки push-уведомлений
    fcm_token = models.CharField(max_length=500, blank=True, null=True, help_text="Firebase FCM токен устройства")
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_notification_type_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def mark_as_read(self):
        """Отметить уведомление как прочитанное"""
        if self.status == 'unread':
            self.status = 'read'
            self.read_at = timezone.now()
            self.save()
    
    def mark_as_deleted(self):
        """Отметить уведомление как удаленное"""
        self.status = 'deleted'
        self.save()
    
    @property
    def is_read(self):
        """Проверить, прочитано ли уведомление"""
        return self.status == 'read'
    
    @property
    def is_deleted(self):
        """Проверить, удалено ли уведомление"""
        return self.status == 'deleted'

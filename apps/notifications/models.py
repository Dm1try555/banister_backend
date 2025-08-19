from django.db import models
from apps.authentication.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=100)  # e.g. "ClientSendBookingNotificationToAdmin"
    data = models.JSONField(default=dict)  # Additional data
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"Notification {self.id} - {self.notification_type} for {self.user.username}"
from django.db import models
from apps.authentication.models import User

class Service(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        indexes = [
            models.Index(fields=['provider', 'created_at']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title

class Schedule(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['provider', 'service', 'day_of_week']
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        indexes = [
            models.Index(fields=['provider', 'day_of_week']),
            models.Index(fields=['service', 'day_of_week']),
            models.Index(fields=['is_available']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.provider.username} - {self.service.title} - {self.get_day_of_week_display()}"
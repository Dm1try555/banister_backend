from django.db import models
from apps.authentication.models import User
from apps.services.models import Service

class Interview(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interviews')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_interviews', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='interviews')
    
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    google_calendar_event_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Interview {self.id} - {self.customer.email}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_bookings')
    
    location = models.CharField(max_length=255, null=True, blank=True)
    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Booking {self.id} - {self.customer.email}"
    
    def save(self, *args, **kwargs):
        if not self.total_price and self.service:
            self.total_price = self.service.price
        super().save(*args, **kwargs)
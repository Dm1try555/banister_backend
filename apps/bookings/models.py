from django.db import models
from core.authentication.models import User
from apps.services.models import Service

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    FREQUENCY_CHOICES = (
        ('one_time', 'One Time'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_bookings')
    
    # Booking details from UI
    location = models.CharField(max_length=255, help_text="Service location/address", null=True, blank=True)
    preferred_date = models.DateField(help_text="Preferred service date", null=True, blank=True)
    preferred_time = models.TimeField(help_text="Preferred service time", null=True, blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='one_time', help_text="Service frequency")
    
    # Combined date and time for actual booking
    scheduled_datetime = models.DateTimeField(help_text="Actual scheduled date and time", null=True, blank=True)
    
    # Status and additional info
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True, help_text="Additional notes from customer")
    
    # Pricing
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Google Calendar integration
    google_calendar_event_id = models.CharField(max_length=255, blank=True, null=True, help_text="Google Calendar event ID")
    calendar_invitations_sent = models.BooleanField(default=False, help_text="Whether calendar invitations were sent")
    calendar_sent_at = models.DateTimeField(blank=True, null=True, help_text="When calendar invitations were sent")
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Booking {self.id} - {self.customer.email} for {self.service.title}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price if not set
        if not self.total_price and self.service:
            self.total_price = self.service.price
        super().save(*args, **kwargs)
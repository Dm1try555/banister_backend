from django.db import models
from apps.authentication.models import User
from apps.bookings.models import Booking

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_payments')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stripe fields
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_transfer_id = models.CharField(max_length=255, blank=True, null=True)  # For provider transfers
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['completed_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.id} - ${self.amount} ({self.status})"
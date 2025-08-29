from core.base.common_imports import *
from apps.authentication.models import User

class Withdrawal(OptimizedUserModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="usd")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_transfer_id = models.CharField(max_length=255, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Withdrawal'
        verbose_name_plural = 'Withdrawals'
    
    def __str__(self):
        return f"Withdrawal {self.id} - ${self.amount} ({self.status})"
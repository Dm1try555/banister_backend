from django.db import models
from apps.authentication.models import User
from apps.services.models import Service


class Interview(models.Model):
    """Interview model for provider interviews"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    provider = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='provider_interviews',
        limit_choices_to={'role': 'provider'}
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name='interviews'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    scheduled_datetime = models.DateTimeField(null=True, blank=True)
    google_calendar_event_id = models.CharField(max_length=255, blank=True)
    google_meet_link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Interview'
        verbose_name_plural = 'Interviews'
        indexes = [
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['scheduled_datetime']),
        ]
    
    def __str__(self):
        return f"Interview: {self.provider.username} - {self.service.title} ({self.status})"


class InterviewRequest(models.Model):
    """Interview request from provider to admin"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    provider = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='interview_requests',
        limit_choices_to={'role': 'provider'}
    )
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name='interview_requests'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    message = models.TextField(help_text="Provider's message to admin")
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Interview Request'
        verbose_name_plural = 'Interview Requests'
        indexes = [
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Interview Request: {self.provider.username} - {self.service.title} ({self.status})"
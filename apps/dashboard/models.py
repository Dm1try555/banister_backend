from django.db import models
from apps.authentication.models import User

class CustomerDashboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_dashboard')
    
    # Calendar settings
    calendar_view_type = models.CharField(max_length=20, default='month', choices=[
        ('day', 'Day'),
        ('week', 'Week'), 
        ('month', 'Month')
    ])
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Profile settings
    vacation_mode = models.BooleanField(default=False)
    vacation_start = models.DateField(blank=True, null=True)
    vacation_end = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Customer Dashboard'
        verbose_name_plural = 'Customer Dashboards'
    
    def __str__(self):
        return f"Customer Dashboard for {self.user.username}"


class ProviderDashboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_dashboard')
    
    # Calendar settings
    calendar_view_type = models.CharField(max_length=20, default='week', choices=[
        ('day', 'Day'),
        ('week', 'Week'), 
        ('month', 'Month')
    ])
    
    # Business settings
    working_hours_start = models.TimeField(default='09:00')
    working_hours_end = models.TimeField(default='17:00')
    
    # Earnings tracking
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    # Availability
    vacation_mode = models.BooleanField(default=False)
    vacation_start = models.DateField(blank=True, null=True)
    vacation_end = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Provider Dashboard'
        verbose_name_plural = 'Provider Dashboards'
    
    def __str__(self):
        return f"Provider Dashboard for {self.user.username}"


class ManagementDashboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='management_dashboard')
    
    # Statistics tracking
    total_customers_managed = models.IntegerField(default=0)
    total_issues_resolved = models.IntegerField(default=0)
    total_issues_pending = models.IntegerField(default=0)
    
    # View preferences
    default_customer_filter = models.CharField(max_length=20, default='all', choices=[
        ('all', 'All Customers'),
        ('active', 'Active Customers'),
        ('my', 'My Customers')
    ])
    
    # Notification settings
    issue_notifications = models.BooleanField(default=True)
    customer_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Management Dashboard'
        verbose_name_plural = 'Management Dashboards'
    
    def __str__(self):
        return f"Management Dashboard for {self.user.username}"


class Issue(models.Model):
    STATUS_CHOICES = (
        ('raised', 'Raised'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='raised')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Users involved
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_issues')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Issue'
        verbose_name_plural = 'Issues'
    
    def __str__(self):
        return f"Issue #{self.id}: {self.title}"
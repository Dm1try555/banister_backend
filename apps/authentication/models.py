from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('supervisor', 'Supervisor'),
        ('customer', 'Customer'),
        ('service_provider', 'Service Provider'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    
    firebase_token = models.CharField(max_length=500, blank=True, null=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    
    provider_verified = models.BooleanField(default=False)
    provider_rating = models.FloatField(default=0.0)
    provider_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_customer(self):
        return self.role == 'customer'
    
    @property
    def is_service_provider(self):
        return self.role == 'service_provider'
    
    @property
    def is_hr(self):
        return self.role == 'hr'
    
    @property 
    def is_supervisor(self):
        return self.role == 'supervisor'
    
    @property
    def is_admin(self):
        return self.role in ['admin', 'super_admin']
    
    @property
    def is_super_admin(self):
        return self.role == 'super_admin'


class AdminPermission(models.Model):
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permissions')
    permission_name = models.CharField(max_length=100)
    can_access = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['admin_user', 'permission_name']
        ordering = ['permission_name']
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.permission_name}: {self.can_access}"
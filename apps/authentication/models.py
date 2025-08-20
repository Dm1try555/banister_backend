from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('provider', 'Provider'),
        ('management', 'Management'),
        ('accountant', 'Accountant'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    # Basic info (first_name, last_name, email, password inherited from AbstractUser)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)  # Address/City
    profile_photo = models.CharField(max_length=255, blank=True, null=True)
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
    
    # Integration tokens
    firebase_token = models.CharField(max_length=500, blank=True, null=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Provider fields (only for providers)
    provider_verified = models.BooleanField(default=False)
    provider_rating = models.FloatField(default=0.0)
    provider_hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_customer(self):
        return self.role == 'customer'
    
    @property
    def is_provider(self):
        return self.role == 'provider'
    
    @property
    def is_management(self):
        return self.role == 'management'
    
    @property 
    def is_accountant(self):
        return self.role == 'accountant'
    
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
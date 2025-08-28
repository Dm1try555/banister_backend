from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string


class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('hr', 'HR'),
        ('supervisor', 'Supervisor'),
        ('customer', 'Customer'),
        ('service_provider', 'Service Provider'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    firebase_token = models.TextField(blank=True, null=True)
    stripe_account_id = models.CharField(max_length=255, blank=True, null=True)
    provider_verified = models.BooleanField(default=False)
    provider_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    provider_hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username


class VerificationCode(models.Model):
    CODE_TYPES = [
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    code_type = models.CharField(max_length=20, choices=CODE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'verification_codes'
        indexes = [
            models.Index(fields=['user', 'code_type']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.code_type} - {self.code}"
    
    @classmethod
    def generate_code(cls):
        """Generate a random 4-digit code"""
        return ''.join(random.choices(string.digits, k=4))
    
    @classmethod
    def create_code(cls, user, code_type, expiry_minutes=10):
        """Create a new verification code"""
        # Invalidate any existing codes of the same type for this user
        cls.objects.filter(user=user, code_type=code_type, is_used=False).update(is_used=True)
        
        code = cls.generate_code()
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        return cls.objects.create(
            user=user,
            code=code,
            code_type=code_type,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """Check if the code is still valid (not expired and not used)"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark the code as used"""
        self.is_used = True
        self.save()


class AdminPermission(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_permissions')
    permission_name = models.CharField(max_length=100)
    can_access = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_permissions'
        unique_together = ['admin', 'permission_name']
    
    def __str__(self):
        return f"{self.admin.username} - {self.permission_name}: {self.can_access}"


class UserFCMToken(models.Model):
    """Model to store user's Firebase Cloud Messaging tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_tokens')
    token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=50, choices=[
        ('web', 'Web'),
        ('android', 'Android'),
        ('ios', 'iOS'),
    ], default='web')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'FCM Token'
        verbose_name_plural = 'FCM Tokens'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type} ({'active' if self.is_active else 'inactive'})"
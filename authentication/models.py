from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
# ProfilePhoto импортируется по требованию для избежания циклических импортов


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')  # По умолчанию для суперюзеров
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('provider', 'Provider'),
        ('management', 'Management'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
        ('accountant', 'Accountant'),
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="US phone number format: (XXX) XXX-XXXX")
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='customer')
    password_hash = models.CharField(max_length=128, blank=True, null=True)  # For Firebase compatibility
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def has_required_profile_photo(self):
        """Check if user has required profile photo (management and provider)"""
        if self.role in ['provider', 'management', 'admin', 'super_admin', 'accountant']:
            try:
                from file_storage.models import ProfilePhoto
                return ProfilePhoto.objects.filter(user=self, is_active=True).exists()
            except Exception:
                return False
        return True  # Customers can have optional profile photo

    def get_profile_photo_url(self):
        """Get profile photo URL if exists"""
        try:
            from file_storage.models import ProfilePhoto
            profile_photo = ProfilePhoto.objects.filter(user=self, is_active=True).first()
            if profile_photo and profile_photo.file_storage:
                return f"http://localhost:9000/{profile_photo.file_storage.bucket_name}/{profile_photo.file_storage.object_key}"
        except Exception:
            pass
        return None

    def is_admin_role(self):
        """Check if user has admin role"""
        return self.role in ['management', 'admin', 'super_admin', 'accountant']

    def is_super_admin(self):
        """Check if user is super admin"""
        return self.role == 'super_admin'

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=128, blank=False, null=False, default='Name')
    last_name = models.CharField(max_length=128, blank=False, null=False, default='Surname')
    bio = models.TextField(blank=True, max_length=500)  # Limit bio length for US standards
    is_email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class VerificationCode(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    code = models.CharField(max_length=10)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email or self.phone}: {self.code}"

class EmailConfirmationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=64, default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - {self.code} - {'used' if self.is_used else 'unused'}"

class EmailConfirmationToken(models.Model):
    """Token for email confirmation via link"""
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.email} - {'used' if self.is_used else 'unused'}"

    def is_expired(self):
        return timezone.now() > self.expires_at


class PasswordResetCode(models.Model):
    """Simple password reset code via email"""
    email = models.EmailField()
    code = models.CharField(max_length=6)  # 6-digit code
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - {self.code} - {'used' if self.is_used else 'unused'}"

    def is_expired(self):
        # Code expires after 10 minutes
        return timezone.now() > self.created_at + timedelta(minutes=10)


class AdminPermission(models.Model):
    """Permissions configuration for admin users"""
    PERMISSION_CHOICES = (
        ('user_management', 'User Management'),
        ('service_management', 'Service Management'),
        ('booking_management', 'Booking Management'),
        ('payment_management', 'Payment Management'),
        ('withdrawal_management', 'Withdrawal Management'),
        ('document_management', 'Document Management'),
        ('financial_reports', 'Financial Reports'),
        ('system_settings', 'System Settings'),
        ('admin_management', 'Admin Management'),
    )
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_permissions')
    permission = models.CharField(max_length=50, choices=PERMISSION_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_permissions')
    
    class Meta:
        unique_together = ('admin_user', 'permission')
        verbose_name = 'Admin Permission'
        verbose_name_plural = 'Admin Permissions'
    
    def __str__(self):
        return f"{self.admin_user.email} - {self.permission} - {'Active' if self.is_active else 'Inactive'}"
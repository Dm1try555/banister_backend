from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
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
        extra_fields.setdefault('role', 'management')  # По умолчанию для суперюзеров
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('provider', 'Provider'),
        ('management', 'Management'),
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
        if self.role in ['provider', 'management']:
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


class PasswordResetToken(models.Model):
    """Token for password reset via email"""
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.email} - {'used' if self.is_used else 'unused'}"

    def is_expired(self):
        return timezone.now() > self.expires_at
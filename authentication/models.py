from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid

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
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('provider', 'Provider'),
        ('management', 'Management'),
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    role = models.CharField(max_length=25, choices=ROLE_CHOICES, default='customer')
    password_hash = models.CharField(max_length=128, blank=True)  # For Firebase compatibility
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, blank=False, null=False, default='Name')
    last_name = models.CharField(max_length=50, blank=False, null=False, default='Surname')
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    is_email_confirmed = models.BooleanField(default=False)

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
from django.db import models
from django.conf import settings
from authentication.models import User
import uuid
import os
from datetime import datetime

class FileStorage(models.Model):
    """Model for storing file information in MinIO"""
    
    FILE_TYPES = (
        ('profile_photo', 'Profile Photo'),
        ('document', 'Document'),
        ('image', 'Image'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file_name = models.CharField(max_length=255)
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='other')
    bucket_name = models.CharField(max_length=100)
    object_key = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    content_type = models.CharField(max_length=100)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'file_storage'
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_name} ({self.user.email})"
    
    @property
    def file_url(self):
        """Returns URL for file access"""
        from .utils import get_minio_client
        try:
            client = get_minio_client()
            return client.presigned_get_object(
                self.bucket_name, 
                self.object_key, 
                expires=3600  # 1 hour
            )
        except Exception:
            return None
    
    @property
    def public_url(self):
        """Returns public URL for the file"""
        if self.is_public:
            return f"/media/{self.bucket_name}/{self.object_key}"
        return None

class ProfilePhoto(models.Model):
    """Model for user profile photos"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_photo')
    file_storage = models.OneToOneField(FileStorage, on_delete=models.CASCADE, related_name='profile_photo')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profile_photos'
        verbose_name = 'Profile Photo'
        verbose_name_plural = 'Profile Photos'
    
    def __str__(self):
        return f"Profile photo {self.user.email}"
    
    @property
    def photo_url(self):
        """Returns profile photo URL"""
        return self.file_storage.file_url if self.file_storage else None

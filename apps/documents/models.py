from django.db import models
from django.core.files.storage import default_storage
from core.base.common_imports import *
from apps.authentication.models import User


class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
    
    @property
    def file_path(self):
        """Возвращает URL файла"""
        return self.file.url if self.file else ''
    
    def get_file_type(self):
        """Get file type based on extension"""
        # Determine type by extension
        if self.file:
            ext = self.file.name.split('.')[-1].lower()
            if ext in ['pdf', 'doc', 'docx']:
                return 'document'
            elif ext in ['jpg', 'jpeg', 'png', 'gif']:
                return 'image'
            elif ext in ['mp4', 'avi', 'mov']:
                return 'video'
            else:
                return 'other'
        return 'unknown'
    
    @property
    def file_size(self):
        """Возвращает размер файла в байтах"""
        try:
            if self.file and hasattr(self.file, 'size'):
                return self.file.size
            elif self.file and default_storage.exists(self.file.name):
                return default_storage.size(self.file.name)
        except Exception:
            pass
        return 0
    
    @property
    def file_extension(self):
        """Возвращает расширение файла"""
        import os
        return os.path.splitext(self.file.name)[1].lower() if self.file else ''
    
    def __str__(self):
        return self.title
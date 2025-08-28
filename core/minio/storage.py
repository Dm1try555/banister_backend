import os
import uuid
from django.core.files.storage import Storage
from django.conf import settings
from .client import minio_client


class MinioStorage(Storage):
    """Custom storage backend for MinIO"""
    
    def __init__(self):
        self.client = minio_client.client
        self.bucket_name = minio_client.bucket_name
    
    def _open(self, name, mode='rb'):
        """Open file for reading"""
        try:
            from io import BytesIO
            response = self.client.get_object(self.bucket_name, name)
            return BytesIO(response.read())
        except Exception:
            return None
    
    def _save(self, name, content):
        """Save file to MinIO"""
        try:
            # Generate unique filename
            file_extension = os.path.splitext(name)[1]
            unique_name = f"{uuid.uuid4()}{file_extension}"
            
            # Upload to MinIO
            self.client.put_object(
                self.bucket_name,
                unique_name,
                content,
                length=content.size,
                content_type=content.content_type
            )
            
            return unique_name
        except Exception:
            return None
    
    def delete(self, name):
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket_name, name)
        except Exception:
            pass
    
    def exists(self, name):
        """Check if file exists in MinIO"""
        try:
            self.client.stat_object(self.bucket_name, name)
            return True
        except Exception:
            return False
    
    def listdir(self, path):
        """List files in directory"""
        try:
            objects = self.client.list_objects(self.bucket_name, prefix=path, recursive=False)
            files = []
            dirs = set()
            
            for obj in objects:
                if obj.object_name.endswith('/'):
                    dirs.add(obj.object_name.rstrip('/'))
                else:
                    files.append(obj.object_name)
            
            return list(dirs), files
        except Exception:
            return [], []
    
    def size(self, name):
        """Get file size"""
        try:
            stat = self.client.stat_object(self.bucket_name, name)
            return stat.size
        except Exception:
            return 0
    
    def url(self, name):
        """Get file URL"""
        if name:
            return f"http://{os.getenv('MINIO_ENDPOINT')}/{self.bucket_name}/{name}"
        return None
    
    def get_available_name(self, name, max_length=None):
        """Get available filename"""
        if max_length and len(name) > max_length:
            name, ext = os.path.splitext(name)
            name = name[:max_length - len(ext)]
            name = f"{name}{ext}"
        
        # Generate unique name if file exists
        if self.exists(name):
            name, ext = os.path.splitext(name)
            name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        return name
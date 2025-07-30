from rest_framework import serializers
from .models import FileStorage, ProfilePhoto
from authentication.serializers import UserSerializer

class FileStorageSerializer(serializers.ModelSerializer):
    """Serializer for file storage"""
    user = UserSerializer(read_only=True)
    file_url = serializers.ReadOnlyField()
    public_url = serializers.ReadOnlyField()
    
    class Meta:
        model = FileStorage
        fields = [
            'id', 'user', 'file_name', 'original_name', 'file_type',
            'bucket_name', 'object_key', 'file_size', 'content_type',
            'is_public', 'created_at', 'updated_at', 'file_url', 'public_url'
        ]
        read_only_fields = [
            'id', 'user', 'file_name', 'bucket_name', 'object_key',
            'file_size', 'content_type', 'created_at', 'updated_at',
            'file_url', 'public_url'
        ]

class ProfilePhotoSerializer(serializers.ModelSerializer):
    """Serializer for profile photos"""
    user = UserSerializer(read_only=True)
    file_storage = FileStorageSerializer(read_only=True)
    photo_url = serializers.ReadOnlyField()
    
    class Meta:
        model = ProfilePhoto
        fields = [
            'id', 'user', 'file_storage', 'is_active',
            'created_at', 'updated_at', 'photo_url'
        ]
        read_only_fields = [
            'id', 'user', 'file_storage', 'created_at', 'updated_at', 'photo_url'
        ]

class UploadProfilePhotoSerializer(serializers.Serializer):
    """Serializer for uploading profile photo"""
    photo = serializers.ImageField(
        max_length=255,
        allow_empty_file=False,
        use_url=False
    )
    
    def validate_photo(self, value):
        """Validate uploaded image"""
        # Check file size (max 5 MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size must not exceed 5 MB")
        
        # Check file format
        allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError("Only JPEG, PNG, GIF formats are supported")
        
        return value 
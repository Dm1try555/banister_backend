from rest_framework import serializers
from .models import FileStorage, ProfilePhoto
from authentication.serializers import UserSerializer

class SimpleUserSerializer(serializers.ModelSerializer):
    """Simplified user serializer for nested objects to avoid circular dependency"""
    profile_photo_url = serializers.SerializerMethodField()
    has_required_profile_photo = serializers.SerializerMethodField()

    class Meta:
        from authentication.models import User
        model = User
        fields = ['id', 'email', 'phone', 'role', 'profile_photo_url', 'has_required_profile_photo']

    def get_profile_photo_url(self, obj):
        """Get profile photo URL if exists"""
        try:
            profile_photo = ProfilePhoto.objects.filter(user=obj, is_active=True).first()
            if profile_photo:
                return profile_photo.photo_url
        except Exception:
            pass
        return None

    def get_has_required_profile_photo(self, obj):
        """Check if user has required profile photo"""
        if obj.role in ['provider', 'management']:
            try:
                profile_photo = ProfilePhoto.objects.filter(user=obj, is_active=True).first()
                return profile_photo is not None
            except Exception:
                return False
        return True

class FileStorageSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    public_url = serializers.SerializerMethodField()

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

    def get_public_url(self, obj):
        minio_base_url = "http://localhost:9000"  # твой MinIO endpoint
        if obj.bucket_name and obj.object_key:
            return f"{minio_base_url}/{obj.bucket_name}/{obj.object_key}"
        return None



    def get_file_url(self, obj):
        # Можно так же вернуть полный URL или другой путь, если нужно
        return self.get_public_url(obj)

class ProfilePhotoSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    file_storage = FileStorageSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = ProfilePhoto
        fields = [
            'id', 'user', 'file_storage', 'is_active',
            'created_at', 'updated_at', 'photo_url'
        ]
        read_only_fields = [
            'id', 'user', 'file_storage', 'created_at', 'updated_at', 'photo_url'
        ]

    def get_photo_url(self, obj):
        if obj.file_storage:
            # Возвращаем полный публичный URL из file_storage через сериализатор
            return FileStorageSerializer().get_public_url(obj.file_storage)
        return None

class UploadProfilePhotoSerializer(serializers.Serializer):
    """Serializer for uploading profile photo"""
    photo = serializers.ImageField(
        max_length=255,
        allow_empty_file=False,
        use_url=False
    )
    
    def validate_photo(self, value):
        # Check file size (max 5 MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size must not exceed 5 MB")
        
        # Check file format
        allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError("Only JPEG, PNG, GIF formats are supported")
        
        return value

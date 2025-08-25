from core.base.common_imports import *
from core.error_handling import ErrorCode

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    file_path = serializers.ReadOnlyField()
    file_type = serializers.ReadOnlyField()
    file_size = serializers.ReadOnlyField()
    file_extension = serializers.ReadOnlyField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file', 'file_path', 'file_type',
            'file_size', 'file_extension', 'uploaded_by', 'created_at'
        ]
        read_only_fields = ['uploaded_by', 'created_at']


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file']

    def validate_file(self, value):
        if not value:
            ErrorCode.EMPTY_FILE.raise_error()
        
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            ErrorCode.FILE_TOO_LARGE.raise_error()
        
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 'text/plain']
        if value.content_type not in allowed_types:
            ErrorCode.INVALID_FILE_TYPE.raise_error()
        
        return value


class DocumentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['title', 'description']


class DocumentUploadSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField()

    def validate_file(self, value):
        if not value:
            ErrorCode.EMPTY_FILE.raise_error()
        
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            ErrorCode.FILE_TOO_LARGE.raise_error()
        
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif', 'text/plain']
        if value.content_type not in allowed_types:
            ErrorCode.INVALID_FILE_TYPE.raise_error()
        
        return value
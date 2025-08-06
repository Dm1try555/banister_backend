from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
import logging

# Import error handling system
from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import FileStorage, ProfilePhoto
from .serializers import (
    FileStorageSerializer, ProfilePhotoSerializer, UploadProfilePhotoSerializer
)
from .utils import (
    upload_file_to_minio, delete_file_from_minio, resize_image,
    generate_object_key, get_bucket_name_for_file_type,
    validate_image_file, get_file_size_mb, get_minio_client
)

logger = logging.getLogger(__name__)

class MinIOValidationMixin:
    """Mixin for MinIO operation validation"""
    
    def validate_minio_connection(self):
        """Validate MinIO connection before operations"""
        try:
            client = get_minio_client()
            # Try to list buckets to test connection
            client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"MinIO connection validation failed: {str(e)}")
            return False
    
    def validate_file_exists_in_minio(self, bucket_name, object_key):
        """Validate that file exists in MinIO before deletion"""
        try:
            client = get_minio_client()
            # Try to get object info
            client.stat_object(bucket_name, object_key)
            return True
        except Exception as e:
            logger.warning(f"File not found in MinIO: {bucket_name}/{object_key}, error: {str(e)}")
            return False
    
    def validate_bucket_exists(self, bucket_name):
        """Validate that bucket exists"""
        try:
            client = get_minio_client()
            return client.bucket_exists(bucket_name)
        except Exception as e:
            logger.error(f"Error checking bucket existence: {str(e)}")
            return False
    
    def validate_user_permissions(self, user, file_storage):
        """Validate user has permissions to access/modify file"""
        if not file_storage:
            return False
        
        # Check if user owns the file
        if hasattr(file_storage, 'user') and file_storage.user != user:
            logger.warning(f"User {user.id} attempted to access file owned by user {file_storage.user.id}")
            return False
        
        # Check if file belongs to user's profile photo
        if hasattr(file_storage, 'profilephoto') and file_storage.profilephoto.user != user:
            logger.warning(f"User {user.id} attempted to access profile photo of user {file_storage.profilephoto.user.id}")
            return False
        
        return True

class ProfilePhotoUploadView(BaseAPIView, MinIOValidationMixin):
    """Profile photo upload"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['post']
    
    @swagger_auto_schema(
        operation_description="Upload or change profile photo - automatically handles existing photos",
        manual_parameters=[
            openapi.Parameter(
                'photo',
                openapi.IN_FORM,
                description='Profile photo file (JPEG, PNG, GIF, max 5MB)',
                type=openapi.TYPE_FILE,
                required=True
            ),
        ],
        responses={
            200: openapi.Response('Photo uploaded/changed', ProfilePhotoSerializer),
            400: 'Validation error',
            403: 'No permissions',
        },
        tags=['Profile Photos']
    )
    @transaction.atomic
    def post(self, request):
        """Upload profile photo"""
        try:
            # Validate MinIO connection first
            if not self.validate_minio_connection():
                return self.error_response(
                    ErrorCode.FILE_STORAGE_ERROR,
                    'Storage service unavailable'
                )
            
            serializer = UploadProfilePhotoSerializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            photo_file = serializer.validated_data['photo']
            
            # Validate image
            if not validate_image_file(photo_file):
                return self.error_response(
                    ErrorCode.INVALID_FILE_FORMAT,
                    'Invalid image format'
                )
            
            # Check file size
            file_size_mb = get_file_size_mb(photo_file)
            if file_size_mb > 5:
                return self.error_response(
                    ErrorCode.FILE_TOO_LARGE,
                    'File size must not exceed 5 MB'
                )
            
            # Resize image
            resized_image = resize_image(photo_file)
            if not resized_image:
                return self.error_response(
                    ErrorCode.FILE_PROCESSING_ERROR,
                    'Image processing error'
                )
            
            # Generate unique key for file
            object_key = generate_object_key(
                request.user.id, 
                'profile_photo', 
                photo_file.name
            )
            
            bucket_name = get_bucket_name_for_file_type('profile_photo')
            
            # Validate bucket exists
            if not self.validate_bucket_exists(bucket_name):
                return self.error_response(
                    ErrorCode.FILE_STORAGE_ERROR,
                    'Storage bucket not available'
                )
            
            # Upload file to MinIO
            if not upload_file_to_minio(
                resized_image, 
                bucket_name, 
                object_key, 
                'image/jpeg'
            ):
                return self.error_response(
                    ErrorCode.FILE_UPLOAD_ERROR,
                    'Error uploading file to storage'
                )
            
            # Handle existing profile photo
            existing_photo = ProfilePhoto.objects.filter(user=request.user, is_active=True).first()
            if existing_photo:
                # Delete old file from MinIO
                if existing_photo.file_storage:
                    delete_file_from_minio(
                        existing_photo.file_storage.bucket_name,
                        existing_photo.file_storage.object_key
                    )
                # Deactivate old photo
                existing_photo.is_active = False
                existing_photo.save()
            
            # Create file storage record
            file_storage = FileStorage.objects.create(
                bucket_name=bucket_name,
                object_key=object_key,
                file_name=photo_file.name,
                file_size=file_size_mb,
                content_type='image/jpeg'
            )
            
            # Create profile photo record
            profile_photo = ProfilePhoto.objects.create(
                user=request.user,
                file_storage=file_storage,
                is_active=True
            )
            
            logger.info(f"Profile photo uploaded successfully for user {request.user.id}")
            
            return self.success_response(
                data=ProfilePhotoSerializer(profile_photo).data,
                message='Profile photo uploaded successfully'
            )
            
        except Exception as e:
            logger.error(f"Error uploading profile photo for user {request.user.id}: {str(e)}")
            return self.error_response(
                ErrorCode.FILE_UPLOAD_ERROR,
                f'Error uploading profile photo: {str(e)}'
            )

class ProfilePhotoDetailView(BaseAPIView, generics.RetrieveAPIView, MinIOValidationMixin):
    """Get profile photo"""
    serializer_class = ProfilePhotoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']
    
    def get_object(self):
        """Get active profile photo for user"""
        return get_object_or_404(ProfilePhoto, user=self.request.user, is_active=True)
    
    @swagger_auto_schema(
        operation_description="Get profile photo for user",
        responses={
            200: openapi.Response('Profile photo', ProfilePhotoSerializer),
            404: 'Profile photo not found',
        },
        tags=['Profile Photos']
    )
    def get(self, request, *args, **kwargs):
        """Get profile photo"""
        try:
            instance = self.get_object()
            
            # Validate user permissions
            if not self.validate_user_permissions(request.user, instance.file_storage):
                return self.error_response(
                    ErrorCode.PERMISSION_DENIED,
                    'You do not have permission to access this file'
                )
            
            # Validate file exists in MinIO
            if not self.validate_file_exists_in_minio(
                instance.file_storage.bucket_name,
                instance.file_storage.object_key
            ):
                logger.warning(f"File not found in MinIO for user {request.user.id}")
                return self.error_response(
                    ErrorCode.FILE_NOT_FOUND,
                    'Profile photo file not found in storage'
                )
            
            serializer = self.get_serializer(instance)
            logger.info(f"Profile photo retrieved successfully for user {request.user.id}")

            return self.success_response(
                data=serializer.data,
                message='Profile photo retrieved successfully'
            )

        except Http404:
            return self.error_response(
                ErrorCode.PROFILE_PHOTO_NOT_FOUND,
                'Profile photo not found'
            )
        except Exception as e:
            logger.error(f"Error retrieving profile photo for user {request.user.id}: {str(e)}")
            return self.error_response(
                ErrorCode.FILE_RETRIEVE_ERROR,
                f'Error retrieving profile photo: {str(e)}'
            )
            

class ProfilePhotoDeleteView(BaseAPIView, generics.DestroyAPIView, MinIOValidationMixin):
    """Delete profile photo"""
    serializer_class = ProfilePhotoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['delete']
    
    def get_object(self):
        """Get active profile photo for user"""
        return get_object_or_404(ProfilePhoto, user=self.request.user, is_active=True)
    
    @swagger_auto_schema(
        operation_description="Delete profile photo for user",
        responses={
            200: 'Profile photo deleted',
            404: 'Profile photo not found',
        },
        tags=['Profile Photos']
    )
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """Delete profile photo"""
        try:
            # Validate MinIO connection first
            if not self.validate_minio_connection():
                return self.error_response(
                    ErrorCode.FILE_STORAGE_ERROR,
                    'Storage service unavailable'
                )
            
            instance = self.get_object()
            
            # Validate user permissions
            if not self.validate_user_permissions(request.user, instance.file_storage):
                return self.error_response(
                    ErrorCode.PERMISSION_DENIED,
                    'You do not have permission to delete this file'
                )
            
            # Validate file exists in MinIO before deletion
            if not self.validate_file_exists_in_minio(
                instance.file_storage.bucket_name,
                instance.file_storage.object_key
            ):
                logger.warning(f"File not found in MinIO for deletion by user {request.user.id}")
                # Continue with database cleanup even if file doesn't exist in MinIO
            
            # Delete file from MinIO
            if not delete_file_from_minio(
                instance.file_storage.bucket_name,
                instance.file_storage.object_key
            ):
                logger.error(f"Failed to delete file from MinIO for user {request.user.id}")
                return self.error_response(
                    ErrorCode.FILE_DELETE_ERROR,
                    'Error deleting file from storage'
                )
            
            # Delete database records
            instance.file_storage.delete()
            instance.delete()
            
            logger.info(f"Profile photo deleted successfully for user {request.user.id}")
            
            return self.success_response(
                message='Profile photo deleted successfully'
            )
            
        except ProfilePhoto.DoesNotExist:
            return self.error_response(
                ErrorCode.PROFILE_PHOTO_NOT_FOUND,
                'Profile photo not found'
            )
        except Exception as e:
            logger.error(f"Error deleting profile photo for user {request.user.id}: {str(e)}")
            return self.error_response(
                ErrorCode.FILE_DELETE_ERROR,
                f'Error deleting profile photo: {str(e)}'
            )



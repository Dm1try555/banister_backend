from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    PermissionError, ValidationError, NotFoundError
)
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import FileStorage, ProfilePhoto
from .serializers import (
    FileStorageSerializer, ProfilePhotoSerializer, UploadProfilePhotoSerializer
)
from .utils import (
    upload_file_to_minio, delete_file_from_minio, resize_image,
    generate_object_key, get_bucket_name_for_file_type,
    validate_image_file, get_file_size_mb
)

class ProfilePhotoUploadView(BaseAPIView):
    """Profile photo upload"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Upload profile photo",
        request_body=UploadProfilePhotoSerializer,
        responses={
            201: openapi.Response('Photo uploaded', ProfilePhotoSerializer),
            400: 'Validation error',
            403: 'No permissions',
        },
        tags=['Profile Photos']
    )
    @transaction.atomic
    def post(self, request):
        """Upload profile photo"""
        try:
            serializer = UploadProfilePhotoSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            photo_file = serializer.validated_data['photo']
            
            # Validate image
            if not validate_image_file(photo_file):
                return self.error_response(
                    error_number='INVALID_IMAGE',
                    error_message='Invalid image format',
                    status_code=400
                )
            
            # Check file size
            file_size_mb = get_file_size_mb(photo_file)
            if file_size_mb > 5:
                return self.error_response(
                    error_number='FILE_TOO_LARGE',
                    error_message='File size must not exceed 5 MB',
                    status_code=400
                )
            
            # Resize image
            resized_image = resize_image(photo_file)
            if not resized_image:
                return self.error_response(
                    error_number='IMAGE_PROCESSING_ERROR',
                    error_message='Image processing error',
                    status_code=400
                )
            
            # Generate unique key for file
            object_key = generate_object_key(
                request.user.id, 
                'profile_photo', 
                photo_file.name
            )
            
            bucket_name = get_bucket_name_for_file_type('profile_photo')
            
            # Upload file to MinIO
            if not upload_file_to_minio(
                resized_image, 
                bucket_name, 
                object_key, 
                'image/jpeg'
            ):
                return self.error_response(
                    error_number='UPLOAD_ERROR',
                    error_message='File upload error',
                    status_code=500
                )
            
            # Create database record
            file_storage = FileStorage.objects.create(
                user=request.user,
                file_name=f"profile_photo_{request.user.id}",
                original_name=photo_file.name,
                file_type='profile_photo',
                bucket_name=bucket_name,
                object_key=object_key,
                file_size=len(resized_image.getvalue()),
                content_type='image/jpeg',
                is_public=True
            )
            
            # # Deactivate previous profile photo
            # ProfilePhoto.objects.filter(user=request.user).delete()  # удаляем старую запись

            
            # Create new profile photo record
            profile_photo, created = ProfilePhoto.objects.update_or_create(
                user=request.user,
                defaults={
                    'file_storage': file_storage,
                    'is_active': True
                }
            )
                        
            return self.success_response(
                data=ProfilePhotoSerializer(profile_photo).data,
                message='Profile photo uploaded successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PROFILE_PHOTO_UPLOAD_ERROR',
                error_message=f'Error uploading profile photo: {str(e)}',
                status_code=500
            )

class ProfilePhotoDetailView(BaseAPIView, generics.RetrieveAPIView):
    """Get profile photo"""
    serializer_class = ProfilePhotoSerializer
    permission_classes = [IsAuthenticated]
    
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
            serializer = self.get_serializer(instance)

            return self.success_response(
                data=serializer.data,
                message='Profile photo retrieved successfully'
            )

        except Http404:
            return self.error_response(
                error_number='PROFILE_PHOTO_NOT_FOUND',
                error_message='Profile photo not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='PROFILE_PHOTO_RETRIEVE_ERROR',
                error_message=f'Error retrieving profile photo: {str(e)}',
                status_code=500
            )
            

class ProfilePhotoDeleteView(BaseAPIView, generics.DestroyAPIView):
    """Delete profile photo"""
    serializer_class = ProfilePhotoSerializer
    permission_classes = [IsAuthenticated]
    
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
            instance = self.get_object()
            
            # Delete file from MinIO
            if not delete_file_from_minio(
                instance.file_storage.bucket_name,
                instance.file_storage.object_key
            ):
                return self.error_response(
                    error_number='DELETE_ERROR',
                    error_message='Error deleting file from storage',
                    status_code=500
                )
            
            # Delete database records
            instance.file_storage.delete()
            instance.delete()
            
            return self.success_response(
                message='Profile photo deleted successfully'
            )
            
        except ProfilePhoto.DoesNotExist:
            return self.error_response(
                error_number='PROFILE_PHOTO_NOT_FOUND',
                error_message='Profile photo not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='PROFILE_PHOTO_DELETE_ERROR',
                error_message=f'Error deleting profile photo: {str(e)}',
                status_code=500
            )

class QuickProfilePhotoChangeView(BaseAPIView):
    """Quick profile photo change with preview"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Quick change profile photo with preview",
        request_body=UploadProfilePhotoSerializer,
        responses={
            200: openapi.Response('Photo changed', ProfilePhotoSerializer),
            400: 'Validation error',
            403: 'No permissions',
        },
        tags=['Profile Photos']
    )
    @transaction.atomic
    def post(self, request):
        """Quick change profile photo"""
        try:
            serializer = UploadProfilePhotoSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            photo_file = serializer.validated_data['photo']
            
            # Validate image
            if not validate_image_file(photo_file):
                return self.error_response(
                    error_number='INVALID_IMAGE',
                    error_message='Invalid image format',
                    status_code=400
                )
            
            # Check file size
            file_size_mb = get_file_size_mb(photo_file)
            if file_size_mb > 5:
                return self.error_response(
                    error_number='FILE_TOO_LARGE',
                    error_message='File size must not exceed 5 MB',
                    status_code=400
                )
            
            # Resize image
            resized_image = resize_image(photo_file)
            if not resized_image:
                return self.error_response(
                    error_number='IMAGE_PROCESSING_ERROR',
                    error_message='Image processing error',
                    status_code=400
                )
            
            # Generate unique key for file
            object_key = generate_object_key(
                request.user.id, 
                'profile_photo', 
                photo_file.name
            )
            
            bucket_name = get_bucket_name_for_file_type('profile_photo')
            
            # Upload file to MinIO
            if not upload_file_to_minio(
                resized_image, 
                bucket_name, 
                object_key, 
                'image/jpeg'
            ):
                return self.error_response(
                    error_number='UPLOAD_ERROR',
                    error_message='File upload error',
                    status_code=500
                )
            
            # Create database record
            file_storage = FileStorage.objects.create(
                user=request.user,
                file_name=f"profile_photo_{request.user.id}",
                original_name=photo_file.name,
                file_type='profile_photo',
                bucket_name=bucket_name,
                object_key=object_key,
                file_size=len(resized_image.getvalue()),
                content_type='image/jpeg',
                is_public=True
            )
            
            # Deactivate previous profile photo and delete old file
            old_profile_photo = ProfilePhoto.objects.filter(user=request.user, is_active=True).first()
            if old_profile_photo:
                # Delete old file from MinIO
                delete_file_from_minio(
                    old_profile_photo.file_storage.bucket_name,
                    old_profile_photo.file_storage.object_key
                )
                # Deactivate old photo
                old_profile_photo.is_active = False
                old_profile_photo.save()
                # Delete old file storage record
                old_profile_photo.file_storage.delete()
            
            # Create new profile photo record
            profile_photo = ProfilePhoto.objects.create(
                user=request.user,
                file_storage=file_storage,
                is_active=True
            )
            
            return self.success_response(
                data=ProfilePhotoSerializer(profile_photo).data,
                message='Profile photo changed successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PROFILE_PHOTO_CHANGE_ERROR',
                error_message=f'Error changing profile photo: {str(e)}',
                status_code=500
            )

from rest_framework import mixins, generics
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import logging

from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode
from .serializers import (
    UserSerializer, ProfileSerializer, CustomerUserSerializer, 
    ProviderUserSerializer, ManagementUserSerializer
)
from .models import User, Profile
from core.file_storage.models import ProfilePhoto

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class ProfileView(BaseAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'delete']

    def get_serializer_class(self):
        """Return appropriate serializer based on user role"""
        user = self.request.user
        if user.role == 'customer':
            return CustomerUserSerializer
        elif user.role == 'provider':
            return ProviderUserSerializer
        elif user.role == 'management':
            return ManagementUserSerializer
        else:
            return UserSerializer

    def get_object(self):
        """Get current user"""
        return self.request.user

    @swagger_auto_schema(
        operation_description="Get user profile",
        responses={
            200: openapi.Response('Profile retrieved successfully', UserSerializer),
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Profile'])
    def get(self, request):
        """Get user profile"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            logger.info(f"Profile retrieved for user: {request.user.email}")
            
            return self.success_response(
                data=serializer.data,
                message='Profile retrieved successfully'
            )
        except Exception as e:
            logger.error(f"Error retrieving profile for user {request.user.email}: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Error retrieving profile: {str(e)}'
            )

    @swagger_auto_schema(
        operation_description="Update user profile (full update) - Role-specific fields. Note: Role cannot be changed.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING, description='Role cannot be changed'),
                'profile': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'bio': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                ),
                'provider_profile': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Only available for provider users',
                    properties={
                        'experience_years': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'hourly_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                    }
                ),
            }
        ),
        responses={
            200: openapi.Response('Profile updated successfully', UserSerializer),
            400: 'Validation error, role change not allowed, or profile photo required for providers/managers',
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Profile'])
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """Update user profile"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=False)
            
            if not serializer.is_valid():
                serializer.is_valid(raise_exception=True)
            
            # Check if role is being changed
            if 'role' in request.data and request.data['role'] != instance.role:
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Role cannot be changed'
                )
            
            # Check profile photo requirement for providers and managers
            if instance.role in ['provider', 'management']:
                try:
                    profile_photo = ProfilePhoto.objects.get(user=instance, is_active=True)
                    if not profile_photo:
                        return self.error_response(
                            ErrorCode.USER_DELETED,
                            'Profile photo is required for providers and managers'
                        )
                except ProfilePhoto.DoesNotExist:
                    return self.error_response(
                        ErrorCode.USER_DELETED,
                        'Profile photo is required for providers and managers'
                    )
            
            serializer.save()
            
            logger.info(f"Profile updated for user: {request.user.email}")
            
            return self.success_response(
                data=serializer.data,
                message='Profile updated successfully'
            )
        except Exception as e:
            logger.error(f"Error updating profile for user {request.user.email}: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Error updating profile: {str(e)}'
            )

    @swagger_auto_schema(
        operation_description="Delete user account (completely removes user and all associated data)",
        responses={
            204: 'User account deleted successfully',
            400: 'Profile photo required for providers/managers',
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Profile'])
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """Delete user account"""
        try:
            instance = self.get_object()
            
            # Check profile photo requirement for providers and managers
            if instance.role in ['provider', 'management']:
                try:
                    profile_photo = ProfilePhoto.objects.get(user=instance, is_active=True)
                    if not profile_photo:
                        return self.error_response(
                            ErrorCode.USER_DELETED,
                            'Profile photo is required for providers and managers'
                        )
                except ProfilePhoto.DoesNotExist:
                    return self.error_response(
                        ErrorCode.USER_DELETED,
                        'Profile photo is required for providers and managers'
                    )
            
            # Delete user (this will cascade to related objects)
            user_email = instance.email
            instance.delete()
            
            logger.info(f"User account deleted: {user_email}")
            
            return self.success_response(
                message='User account deleted successfully'
            )
        except Exception as e:
            logger.error(f"Error deleting user account {request.user.email}: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Error deleting user account: {str(e)}'
            ) 
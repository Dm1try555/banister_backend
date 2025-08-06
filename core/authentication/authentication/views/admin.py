from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import logging

from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode
from .serializers import (
    UserSerializer, AdminUserSerializer, AdminProfileUpdateSerializer, 
    AdminPermissionUpdateSerializer, AdminPermissionSerializer
)
from .models import User, AdminPermission

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class AdminProfileView(BaseAPIView):
    """Admin profile management - Admin users only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put']
    
    def check_admin_permissions(self, user):
        """Check if user has admin permissions"""
        if user.role not in ['admin', 'super_admin']:
            return False
        return True

    @swagger_auto_schema(
        operation_description="Get admin profile (Admin users only)",
        responses={
            200: openapi.Response('Admin profile retrieved', AdminUserSerializer),
            400: 'Validation error',
            403: 'Access denied - only admin users can view their profile',
            404: 'Profile not found',
            500: 'Server error'
        },
        tags=['Admin'])
    def get(self, request):
        """Get admin profile"""
        try:
            if not self.check_admin_permissions(request.user):
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Access denied - only admin users can view their profile'
                )
            
            serializer = AdminUserSerializer(request.user)
            
            logger.info(f"Admin profile retrieved for user: {request.user.email}")
            
            return self.success_response(
                data=serializer.data,
                message='Admin profile retrieved successfully'
            )
        except Exception as e:
            logger.error(f"Error retrieving admin profile for user {request.user.email}: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Error retrieving admin profile: {str(e)}'
            )

    @swagger_auto_schema(
        operation_description="Update admin profile (Admin users only)",
        request_body=AdminProfileUpdateSerializer,
        responses={
            200: openapi.Response('Admin profile updated', AdminUserSerializer),
            400: 'Validation error',
            403: 'Access denied - only admin users can update their profile',
            404: 'Profile not found',
            500: 'Server error'
        },
        tags=['Admin'])
    @transaction.atomic
    def put(self, request):
        """Update admin profile"""
        try:
            if not self.check_admin_permissions(request.user):
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Access denied - only admin users can update their profile'
                )
            
            serializer = AdminProfileUpdateSerializer(request.user, data=request.data, partial=True)
            
            if not serializer.is_valid():
                serializer.is_valid(raise_exception=True)
            
            serializer.save()
            
            logger.info(f"Admin profile updated for user: {request.user.email}")
            
            return self.success_response(
                data=serializer.data,
                message='Admin profile updated successfully'
            )
        except Exception as e:
            logger.error(f"Error updating admin profile for user {request.user.email}: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Error updating admin profile: {str(e)}'
            )

class AdminPermissionManagementView(BaseAPIView):
    """Manage admin permissions (grant/revoke) - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'get', 'delete']
    
    def check_super_admin_permissions(self, user):
        """Check if user has super admin permissions"""
        return user.role == 'super_admin'

    @swagger_auto_schema(
        operation_description="Grant or revoke permissions for admin users (Super Admin only)",
        request_body=AdminPermissionUpdateSerializer,
        responses={
            200: openapi.Response('Permissions updated successfully'),
            400: 'Validation error or invalid permission',
            403: 'Access denied - only super admin can manage permissions',
            404: 'Admin user not found',
            500: 'Server error'
        },
        tags=['Admin'])
    @transaction.atomic
    def post(self, request):
        """Grant permissions to admin user"""
        try:
            if not self.check_super_admin_permissions(request.user):
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Access denied - only super admin can manage permissions'
                )
            
            serializer = AdminPermissionUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                serializer.is_valid(raise_exception=True)
            
            admin_user_id = serializer.validated_data['admin_user_id']
            permissions = serializer.validated_data['permissions']
            action = serializer.validated_data.get('action', 'grant')
            
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Admin user not found'
                )
            
            # Grant or revoke permissions
            for permission in permissions:
                if action == 'grant':
                    AdminPermission.objects.get_or_create(
                        user=admin_user,
                        permission=permission
                    )
                elif action == 'revoke':
                    AdminPermission.objects.filter(
                        user=admin_user,
                        permission=permission
                    ).delete()
            
            logger.info(f"Permissions {action}ed for admin user {admin_user.email}: {permissions}")
            
            return self.success_response(
                message=f'Permissions {action}ed successfully'
            )
        except Exception as e:
            logger.error(f"Error managing permissions: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Error managing permissions: {str(e)}'
            )

    @swagger_auto_schema(
        operation_description="Get permissions for specific admin user (Super Admin only)",
        manual_parameters=[
            openapi.Parameter(
                'admin_user_id',
                openapi.IN_QUERY,
                description='Admin user ID',
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: openapi.Response('Admin permissions retrieved', AdminPermissionSerializer),
            403: 'Access denied - only super admin can view permissions',
            404: 'Admin user not found',
            500: 'Server error'
        },
        tags=['Admin'])
    def get(self, request):
        """Get permissions for admin user"""
        try:
            if not self.check_super_admin_permissions(request.user):
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Access denied - only super admin can view permissions'
                )
            
            admin_user_id = request.GET.get('admin_user_id')
            if not admin_user_id:
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Admin user ID is required'
                )
            
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Admin user not found'
                )
            
            permissions = AdminPermission.objects.filter(user=admin_user)
            serializer = AdminPermissionSerializer(permissions, many=True)
            
            logger.info(f"Permissions retrieved for admin user: {admin_user.email}")
            
            return self.success_response(
                data=serializer.data,
                message='Admin permissions retrieved successfully'
            )
        except Exception as e:
            logger.error(f"Error retrieving permissions: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Error retrieving permissions: {str(e)}'
            )

    @swagger_auto_schema(
        operation_description="Delete specific permission for admin user (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['admin_user_id', 'permission'],
            properties={
                'admin_user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Admin user ID'),
                'permission': openapi.Schema(type=openapi.TYPE_STRING, description='Permission to delete'),
            }
        ),
        responses={
            200: openapi.Response('Permission deleted successfully'),
            400: 'Validation error',
            403: 'Access denied - only super admin can delete permissions',
            404: 'Admin user or permission not found',
            500: 'Server error'
        },
        tags=['Admin'])
    @transaction.atomic
    def delete(self, request):
        """Delete specific permission for admin user"""
        try:
            if not self.check_super_admin_permissions(request.user):
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Access denied - only super admin can delete permissions'
                )
            
            admin_user_id = request.data.get('admin_user_id')
            permission = request.data.get('permission')
            
            if not admin_user_id or not permission:
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Admin user ID and permission are required'
                )
            
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Admin user not found'
                )
            
            # Delete permission
            deleted_count = AdminPermission.objects.filter(
                user=admin_user,
                permission=permission
            ).delete()[0]
            
            if deleted_count == 0:
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Permission not found'
                )
            
            logger.info(f"Permission '{permission}' deleted for admin user: {admin_user.email}")
            
            return self.success_response(
                message='Permission deleted successfully'
            )
        except Exception as e:
            logger.error(f"Error deleting permission: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Error deleting permission: {str(e)}'
            ) 
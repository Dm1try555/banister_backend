from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import AdminIssue
from .serializers import AdminIssueSerializer
from authentication.models import User
from authentication.serializers import UserSerializer
from error_handling.views import BaseAPIView
from error_handling.exceptions import CustomPermissionError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class AdminUserListView(BaseAPIView, generics.ListAPIView):
    """List of all users for admin"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get list of all users (admin only)",
        responses={
            200: openapi.Response('User list', UserSerializer(many=True)),
        },
        tags=['Users']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='User list retrieved successfully'
        )

class AdminUserDetailView(BaseAPIView, generics.RetrieveDestroyAPIView):
    """Detailed information and deletion of user for admin"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get detailed information about user by ID (admin only)",
        responses={
            200: openapi.Response('User information', UserSerializer),
            404: 'User not found',
        },
        tags=['Users']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='User information retrieved successfully'
            )
            
        except User.DoesNotExist:
            return self.error_response(
                error_number='USER_NOT_FOUND',
                error_message='User not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_USER_RETRIEVE_ERROR',
                error_message=f'Error retrieving user information: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Delete user by ID (admin only)",
        responses={
            200: 'User deleted',
            404: 'User not found',
        },
        tags=['Users']
    )
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            
            return self.success_response(
                message='User deleted successfully'
            )
            
        except User.DoesNotExist:
            return self.error_response(
                error_number='USER_NOT_FOUND',
                error_message='User not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_USER_DELETE_ERROR',
                error_message=f'Error deleting user: {str(e)}',
                status_code=500
            )

class AdminIssueListView(BaseAPIView, generics.ListAPIView):
    """List of all issues for admin"""
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get list of all issues (admin only)",
        responses={
            200: openapi.Response('Issue list', AdminIssueSerializer(many=True)),
        },
        tags=['Admin']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return self.success_response(
            data=serializer.data,
            message='Issue list retrieved successfully'
        )

class AdminIssueCreateView(BaseAPIView, generics.CreateAPIView):
    """Create new issue for admin"""
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Create new issue (admin only)",
        request_body=AdminIssueSerializer,
        responses={
            201: openapi.Response('Issue created', AdminIssueSerializer),
            400: 'Validation error',
        },
        tags=['Admin']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Issue created successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_CREATE_ERROR',
                error_message=f'Error creating issue: {str(e)}',
                status_code=500
            )

class AdminIssueDetailView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    """Detailed information, update, and deletion of issue for admin"""
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get detailed information about issue by ID (admin only)",
        responses={
            200: openapi.Response('Issue information', AdminIssueSerializer),
            404: 'Issue not found',
        },
        tags=['Admin']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Issue information retrieved successfully'
            )
            
        except AdminIssue.DoesNotExist:
            return self.error_response(
                error_number='ISSUE_NOT_FOUND',
                error_message='Issue not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_RETRIEVE_ERROR',
                error_message=f'Error retrieving issue information: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Update issue by ID (admin only)",
        request_body=AdminIssueSerializer,
        responses={
            200: openapi.Response('Issue updated', AdminIssueSerializer),
            400: 'Validation error',
            404: 'Issue not found',
        },
        tags=['Admin']
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            serializer.save()
            return self.success_response(
                data=serializer.data,
                message='Issue updated successfully'
            )
        except AdminIssue.DoesNotExist:
            return self.error_response(
                error_number='ISSUE_NOT_FOUND',
                error_message='Issue not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_UPDATE_ERROR',
                error_message=f'Error updating issue: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Delete issue by ID (admin only)",
        responses={
            200: 'Issue deleted',
            404: 'Issue not found',
        },
        tags=['Admin']
    )
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return self.success_response(
                message='Issue deleted successfully'
            )
        except AdminIssue.DoesNotExist:
            return self.error_response(
                error_number='ISSUE_NOT_FOUND',
                error_message='Issue not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_DELETE_ERROR',
                error_message=f'Error deleting issue: {str(e)}',
                status_code=500
            )

class AdminIssueListCreateView(BaseAPIView, generics.ListCreateAPIView):
    """List and create issues for admin"""
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get list of all issues (admin only)",
        responses={
            200: openapi.Response('Issue list', AdminIssueSerializer(many=True)),
        },
        tags=['Admin']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message='Issue list retrieved successfully'
        )

    @swagger_auto_schema(
        operation_description="Create new issue (admin only)",
        request_body=AdminIssueSerializer,
        responses={
            201: openapi.Response('Issue created', AdminIssueSerializer),
            400: 'Validation error',
        },
        tags=['Admin']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            self.perform_create(serializer)
            return self.success_response(
                data=serializer.data,
                message='Issue created successfully'
            )
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_ISSUE_CREATE_ERROR',
                error_message=f'Error creating issue: {str(e)}',
                status_code=500
            )

class CustomerListView(BaseAPIView, generics.ListAPIView):
    """List of customers for admin"""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Get customer list (admin)",
        responses={
            200: openapi.Response('Customer list', UserSerializer(many=True)),
        },
        tags=['Admin']
    )
    def get_queryset(self):
        return User.objects.filter(role='customer')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message='Customer list retrieved successfully'
        )

class ProviderListView(BaseAPIView, generics.ListAPIView):
    """List of providers for admin"""
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Get provider list (admin)",
        responses={
            200: openapi.Response('Provider list', UserSerializer(many=True)),
        },
        tags=['Admin']
    )
    def get_queryset(self):
        return User.objects.filter(role='provider')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(
            data=serializer.data,
            message='Provider list retrieved successfully'
        )
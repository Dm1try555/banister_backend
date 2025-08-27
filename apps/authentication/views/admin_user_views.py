from core.base.common_imports import *
from rest_framework.permissions import IsAdminUser
from ..models import User
from ..serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, AdminProfileUpdateSerializer, ToggleVerificationSerializer


class AdminUserViewSet(SwaggerMixin, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'request') or not self.request:
            self.swagger_fake_view = True
    
    def get_serializer_class(self):
        action_serializers = {
            'create': UserCreateSerializer,
            'update': UserUpdateSerializer,
            'partial_update': UserUpdateSerializer,
            'admin_update': AdminProfileUpdateSerializer
        }
        return action_serializers.get(self.action, self.serializer_class)
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.none()
        
        return self._get_role_based_queryset(User, self.request.user)
    
    def perform_create(self, serializer):
        """Create user with permission check"""
        current_user = self.request.user
        new_user_role = serializer.validated_data.get('role', 'customer')
        
        # Check if current user can create users with such role
        if not self._can_create_user_with_role(current_user, new_user_role):
            ErrorCode.PERMISSION_DENIED.raise_error()
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Update user with permission check"""
        current_user = self.request.user
        target_user = serializer.instance
        
        # Check if current user can manage target user
        if not self.can_manage_user(current_user, target_user):
            ErrorCode.PERMISSION_DENIED.raise_error()
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete user with permission check"""
        current_user = self.request.user
        
        # Check if current user can delete target user
        if not self.can_delete_user(current_user, instance):
            ErrorCode.PERMISSION_DENIED.raise_error()
        
        instance.delete()
    
    def _can_create_user_with_role(self, current_user, new_user_role):
        """Check if current user can create users with specified role"""
        if current_user.role == 'super_admin':
            return True  # Super Admin can create all users
        
        if current_user.role == 'admin':
            return new_user_role != 'super_admin'  # Admin cannot create Super Admin
        
        if current_user.role == 'hr':
            return new_user_role in ['supervisor', 'customer', 'service_provider']
        
        if current_user.role == 'supervisor':
            return new_user_role in ['customer', 'service_provider']
        
        # Customer and Service Provider cannot create users
        return False
    
    def can_manage_user(self, current_user, target_user):
        """Check if current user can manage target user"""
        if current_user.role == 'super_admin':
            return True  # Super Admin can manage all users
        
        if current_user.role == 'admin':
            return target_user.role != 'super_admin'  # Admin cannot manage Super Admin
        
        if current_user.role == 'hr':
            return target_user.role in ['supervisor', 'customer', 'service_provider']
        
        if current_user.role == 'supervisor':
            return target_user.role in ['customer', 'service_provider']
        
        # Customer and Service Provider cannot manage other users
        return False
    
    def can_delete_user(self, current_user, target_user):
        """Check if current user can delete target user"""
        # Prevent self-deletion
        if current_user.id == target_user.id:
            return False
        
        if current_user.role == 'super_admin':
            return True  # Super Admin can delete all users (except self)
        
        if current_user.role == 'admin':
            return target_user.role not in ['super_admin', 'admin']  # Admin cannot delete Super Admin or other Admins
        
        if current_user.role == 'hr':
            return target_user.role in ['supervisor', 'customer', 'service_provider']
        
        if current_user.role == 'supervisor':
            return target_user.role in ['customer', 'service_provider']
        
        # Customer and Service Provider cannot delete users
        return False
    
    def _get_role_based_queryset(self, model, user):
        """Filter queryset based on user role"""
        if user.role == 'super_admin':
            return model.objects.all()
        elif user.role == 'admin':
            return model.objects.exclude(role='super_admin')
        elif user.role == 'hr':
            return model.objects.filter(role__in=['supervisor', 'customer', 'service_provider'])
        elif user.role == 'supervisor':
            return model.objects.filter(role__in=['customer', 'service_provider'])
        else:
            return model.objects.filter(id=user.id)
    
    @swagger_auto_schema(
        operation_description="Update admin profile information",
        request_body=AdminProfileUpdateSerializer,
        responses={
            200: USER_RESPONSE_SCHEMA,
            400: ERROR_400_SCHEMA,
            404: ERROR_404_SCHEMA
        }
    )
    @action(detail=True, methods=['patch'])
    def admin_update(self, request, pk=None):
        user = self.get_object()
        serializer = AdminProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Toggle user verification status",
        request_body=ToggleVerificationSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'verified': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    @action(detail=True, methods=['post'])
    def toggle_verification(self, request, pk=None):
        # Get user directly without queryset filtering for this admin action
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            ErrorCode.USER_NOT_FOUND.raise_error()
        
        # Check if current user can manage target user
        if not self.can_manage_user(request.user, user):
            ErrorCode.PERMISSION_DENIED.raise_error()
            
        serializer = ToggleVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        verification_type = serializer.validated_data['type']
        
        if verification_type == 'email':
            user.email_verified = not user.email_verified
        elif verification_type == 'provider':
            user.provider_verified = not user.provider_verified
        
        user.save()
        return Response({
            'status': f'{verification_type} verification toggled',
            'verified': getattr(user, f'{verification_type}_verified')
        })
    
    def destroy(self, request, *args, **kwargs):
        """Delete user (only for authorized roles)"""
        user = self.get_object()
        current_user = request.user
        
        # Check if current user can delete target user
        if not self.can_delete_user(current_user, user):
            ErrorCode.PERMISSION_DENIED.raise_error()
        
        # Delete user
        user.delete()
        
        return Response({
            'message': f'User {user.username} deleted successfully'
        }, status=status.HTTP_200_OK) 
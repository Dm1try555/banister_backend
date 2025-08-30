from core.base.common_imports import *
from ..models import User, AdminPermission
from ..serializers import AdminPermissionSerializer, AdminPermissionManageSerializer


class AdminPermissionListView(OptimizedListCreateView):
    """List and create admin permissions"""
    permission_classes = [IsAuthenticated]
    serializer_class = AdminPermissionSerializer
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AdminPermission.objects.none()
        
        # Only super_admin can manage permissions
        if not self.request.user.role == 'super_admin':
            return AdminPermission.objects.none()
        return AdminPermission.objects.all()
    
    @swagger_auto_schema(
        operation_description="List all admin permissions",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'results': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    )
                }
            ),
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA
        }
    )
    def get(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create new admin permission",
        request_body=AdminPermissionManageSerializer,
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'admin': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'permission_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'can_access': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA
        }
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        
        serializer = AdminPermissionManageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        admin_id = serializer.validated_data['admin_id']
        permission_name = serializer.validated_data['permission_name']
        can_access = serializer.validated_data['can_access']
        
        # Check if admin exists and is actually an admin
        try:
            admin = User.objects.get(id=admin_id)
            if admin.role not in ['admin', 'super_admin']:
                raise CustomValidationError(ErrorCode.INVALID_DATA)
        except User.DoesNotExist:
            raise CustomValidationError(ErrorCode.USER_NOT_FOUND)
        
        # Create or update permission
        permission, created = AdminPermission.objects.get_or_create(
            admin=admin,
            permission_name=permission_name,
            defaults={'can_access': can_access}
        )
        
        if not created:
            permission.can_access = can_access
            permission.save()
        
        return Response(AdminPermissionSerializer(permission).data, status=status.HTTP_201_CREATED)


class AdminPermissionDetailView(OptimizedRetrieveUpdateDestroyView):
    """Retrieve, update or delete admin permission"""
    permission_classes = [IsAuthenticated]
    serializer_class = AdminPermissionSerializer
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AdminPermission.objects.none()
        
        # Only super_admin can manage permissions
        if not self.request.user.role == 'super_admin':
            return AdminPermission.objects.none()
        return AdminPermission.objects.all()
    
    @swagger_auto_schema(
        operation_description="Get admin permission details",
        responses={
            200: AdminPermissionSerializer,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        }
    )
    def get(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update admin permission",
        request_body=AdminPermissionManageSerializer,
        responses={
            200: AdminPermissionSerializer,
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        }
    )
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        
        permission = self.get_object()
        serializer = AdminPermissionManageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        admin_id = serializer.validated_data['admin_id']
        permission_name = serializer.validated_data['permission_name']
        can_access = serializer.validated_data['can_access']
        
        # Check if admin exists and is actually an admin
        try:
            admin = User.objects.get(id=admin_id)
            if admin.role not in ['admin', 'super_admin']:
                raise CustomValidationError(ErrorCode.INVALID_DATA)
        except User.DoesNotExist:
            raise CustomValidationError(ErrorCode.USER_NOT_FOUND)
        
        # Update permission
        permission.admin = admin
        permission.permission_name = permission_name
        permission.can_access = can_access
        permission.save()
        
        return Response(AdminPermissionSerializer(permission).data)
    
    @swagger_auto_schema(
        operation_description="Partially update admin permission",
        request_body=AdminPermissionManageSerializer,
        responses={
            200: AdminPermissionSerializer,
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        }
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        
        permission = self.get_object()
        serializer = AdminPermissionManageSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Update only provided fields
        if 'admin_id' in serializer.validated_data:
            admin_id = serializer.validated_data['admin_id']
            try:
                admin = User.objects.get(id=admin_id)
                if admin.role not in ['admin', 'super_admin']:
                    raise CustomValidationError(ErrorCode.INVALID_DATA)
                permission.admin = admin
            except User.DoesNotExist:
                raise CustomValidationError(ErrorCode.USER_NOT_FOUND)
        
        if 'permission_name' in serializer.validated_data:
            permission.permission_name = serializer.validated_data['permission_name']
        
        if 'can_access' in serializer.validated_data:
            permission.can_access = serializer.validated_data['can_access']
        
        permission.save()
        
        return Response(AdminPermissionSerializer(permission).data)
    
    @swagger_auto_schema(
        operation_description="Delete admin permission",
        responses={
            204: openapi.Schema(type=openapi.TYPE_OBJECT),
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        }
    )
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        
        permission = self.get_object()
        permission.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminPermissionByAdminView(OptimizedListCreateView):
    """Get all permissions for a specific admin"""
    permission_classes = [IsAuthenticated]
    serializer_class = AdminPermissionSerializer
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return AdminPermission.objects.none()
        
        # Only super_admin can view permissions
        if not self.request.user.role == 'super_admin':
            return AdminPermission.objects.none()
        
        admin_id = self.kwargs.get('admin_id')
        return AdminPermission.objects.filter(admin_id=admin_id)
    
    @swagger_auto_schema(
        operation_description="Get all permissions for specific admin",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'results': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_OBJECT)
                    )
                }
            ),
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA
        }
    )
    def get(self, request, *args, **kwargs):
        if request.user.role != 'super_admin':
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        
        # Check if admin exists
        admin_id = self.kwargs.get('admin_id')
        try:
            admin = User.objects.get(id=admin_id)
            if admin.role not in ['admin', 'super_admin']:
                raise CustomValidationError(ErrorCode.INVALID_DATA)
        except User.DoesNotExist:
            raise CustomValidationError(ErrorCode.USER_NOT_FOUND)
        
        return super().get(request, *args, **kwargs)


# View instances
admin_permission_list = AdminPermissionListView.as_view()
admin_permission_detail = AdminPermissionDetailView.as_view()
admin_permission_by_admin = AdminPermissionByAdminView.as_view()
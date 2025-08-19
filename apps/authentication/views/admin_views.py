from .base import *


class UpdateAdminProfileView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Update admin profile (only first_name and last_name)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
            }
        ),
        responses={
            200: openapi.Response(description="Profile updated successfully"),
            403: openapi.Response(description="Permission denied")
        }
    )
    def get_object(self):
        user = self.request.user
        if not user.is_admin:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Permission denied')
        return user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Ограничиваем поля только first_name и last_name
        allowed_fields = {'first_name', 'last_name'}
        filtered_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        serializer = self.get_serializer(instance, data=filtered_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({'message': 'Profile updated successfully', 'user': serializer.data})


class ManageAdminPermissionsView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Grant or revoke admin permissions (Super admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['admin_id', 'permission_name', 'can_access'],
            properties={
                'admin_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Admin user ID'),
                'permission_name': openapi.Schema(type=openapi.TYPE_STRING, description='Permission name'),
                'can_access': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Grant or revoke access'),
            }
        ),
        responses={
            200: openapi.Response(description="Permission updated"),
            403: openapi.Response(description="Permission denied"),
            404: openapi.Response(description="Admin not found")
        }
    )
    def post(self, request):
        if not request.user.is_super_admin:
            return Response({'error': 'Only super admin can manage permissions'}, status=status.HTTP_403_FORBIDDEN)
        
        admin_id = request.data.get('admin_id')
        permission_name = request.data.get('permission_name')
        can_access = request.data.get('can_access')
        
        try:
            admin_user = User.objects.get(id=admin_id, role='admin')
        except User.DoesNotExist:
            return Response({'error': 'Admin user not found'}, status=status.HTTP_404_NOT_FOUND)
        
        permission, created = AdminPermission.objects.get_or_create(
            admin_user=admin_user,
            permission_name=permission_name,
            defaults={'can_access': can_access}
        )
        
        if not created:
            permission.can_access = can_access
            permission.save()
        
        action = 'granted' if can_access else 'revoked'
        return Response({
            'message': f'Permission {permission_name} {action} for {admin_user.username}',
            'permission': AdminPermissionSerializer(permission).data
        })


class GetAdminPermissionsView(generics.ListAPIView):
    serializer_class = AdminPermissionSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get admin permissions",
        responses={
            200: openapi.Response(description="Admin permissions list"),
            403: openapi.Response(description="Permission denied")
        }
    )
    def get_queryset(self):
        if not self.request.user.is_admin:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Access denied')
        
        if self.request.user.is_super_admin:
            return AdminPermission.objects.all()
        else:
            return AdminPermission.objects.filter(admin_user=self.request.user)


# Псевдонимы для обратной совместимости
update_admin_profile = UpdateAdminProfileView.as_view()
manage_admin_permissions = ManageAdminPermissionsView.as_view()
get_admin_permissions = GetAdminPermissionsView.as_view()
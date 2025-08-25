from core.base.common_imports import *
from rest_framework.permissions import IsAdminUser
from ..models import User
from ..serializers import UserSerializer, UserCreateSerializer, UserUpdateSerializer, AdminProfileUpdateSerializer


class AdminUserViewSet(SwaggerMixin, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем флаг для Swagger
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
        # Проверка для Swagger - если пользователь не аутентифицирован
        if not self.request.user.is_authenticated:
            return User.objects.none()
            
        user = self.request.user
        if user.role in ['super_admin', 'admin']:
            return User.objects.all()
        elif user.role in ['hr', 'supervisor']:
            return User.objects.filter(role__in=['customer', 'service_provider'])
        return User.objects.none()
    
    @swagger_auto_schema(
        operation_description="Update admin profile information",
        request_body=AdminProfileUpdateSerializer,
                    responses={
             200: openapi.Schema(
                 type=openapi.TYPE_OBJECT,
                 properties={
                     'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                     'username': openapi.Schema(type=openapi.TYPE_STRING),
                     'email': openapi.Schema(type=openapi.TYPE_STRING),
                     'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                     'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                     'role': openapi.Schema(type=openapi.TYPE_STRING),
                     'phone': openapi.Schema(type=openapi.TYPE_STRING),
                     'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                     'provider_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                     'profile_photo': openapi.Schema(type=openapi.TYPE_STRING),
                     'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                     'last_login': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                 }
             ),
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
        responses={
            200: openapi.Response(
                description="Verification status toggled successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'verified': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: ERROR_400_SCHEMA
        }
    )
    @action(detail=True, methods=['post'])
    def toggle_verification(self, request, pk=None):
        user = self.get_object()
        verification_type = request.data.get('type')
        
        if verification_type == 'email':
            user.email_verified = not user.email_verified
        elif verification_type == 'provider':
            user.provider_verified = not user.provider_verified
        else:
            return Response({'error': 'Invalid verification type'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.save()
        return Response({
            'status': f'{verification_type} verification toggled',
            'verified': getattr(user, f'{verification_type}_verified')
        }) 
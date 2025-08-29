from core.base.common_imports import *
from ..models import User
from ..serializers import AdminUserCreateSerializer, UserSerializer, LoginSerializer
from django.template.loader import render_to_string


class AdminUserRegisterView(OptimizedCreateView):
    """Register new admin users (only for super_admin)"""
    serializer_class = AdminUserCreateSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Register a new admin user (super_admin only)",
        request_body=AdminUserCreateSerializer,
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA
        }
    )
    def post(self, request, *args, **kwargs):
        # Check if user is super_admin
        if request.user.role != 'super_admin':
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        
        return super().post(request, *args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send welcome email
        try:
            self._send_welcome_email(user)
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {e}")
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Admin user registered successfully.'
        }, status=status.HTTP_201_CREATED)
    
    def _send_welcome_email(self, user):
        """Send welcome email to new admin user"""
        try:
            html_message = render_to_string('emails/welcome_email.html', {
                'user': user,
                'is_admin': True
            })
            
            send_mail(
                subject='Welcome to Banister Admin Panel',
                message=f'Welcome {user.first_name}! You have been registered as an admin user.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")


class AdminLoginView(BaseAPIView):
    """Login for admin users (super_admin, admin, hr, supervisor)"""
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Login for admin users with username/email",
        request_body=LoginSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username_or_email = serializer.validated_data['username_or_email']
        password = serializer.validated_data['password']
        
        # Try to authenticate with username first, then with email
        user = authenticate(username=username_or_email, password=password)
        if not user:
            # If username authentication failed, try email
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if not user:
            raise CustomValidationError(ErrorCode.INVALID_CREDENTIALS)
        
        # Check if user has admin role
        admin_roles = ['super_admin', 'admin', 'hr', 'supervisor']
        if user.role not in admin_roles:
            raise CustomValidationError(ErrorCode.PERMISSION_DENIED)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'user': UserSerializer(user).data,
            'access': str(access_token),
            'refresh': str(refresh)
        })


# View instances
admin_user_register = AdminUserRegisterView.as_view()
admin_login = AdminLoginView.as_view()
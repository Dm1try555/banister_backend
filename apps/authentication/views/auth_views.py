from core.base.common_imports import *
from ..models import User
from ..serializers import UserCreateSerializer, LoginSerializer, RefreshSerializer, UserSerializer
from django.template.loader import render_to_string


class RegisterView(CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=UserCreateSerializer,
        responses={
            201: USER_CREATE_RESPONSE_SCHEMA,
            400: ERROR_400_SCHEMA
        }
    )
    def post(self, request, *args, **kwargs):
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
            'message': 'User registered successfully.'
        }, status=status.HTTP_201_CREATED)
    
    def _send_welcome_email(self, user):
        """Send welcome email to new user"""
        try:
            html_message = render_to_string('emails/welcome_email.html', {
                'username': user.username,
                'login_url': f"{settings.FRONTEND_URL}/login" if hasattr(settings, 'FRONTEND_URL') else '/login'
            })
            
            send_mail(
                subject='Welcome to Banister! 🎉',
                message=f'Welcome {user.username}! Thank you for joining Banister.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {e}")


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Login user with username/email and password",
        request_body=LoginSerializer,
        responses={
            200: LOGIN_RESPONSE_SCHEMA,
            400: ERROR_400_SCHEMA
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
        
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Refresh access token using refresh token",
        request_body=RefreshSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            refresh = RefreshToken(serializer.validated_data['refresh'])
            return Response({
                'access': str(refresh.access_token)
            })
        except Exception:
            raise CustomValidationError(ErrorCode.INVALID_TOKEN)
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
            201: openapi.Response(
                description="User registered successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
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
                        'tokens': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                                'access': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Validation errors",
                examples={
                    "application/json": {
                        "1012: Passwords do not match": {
                            "statusCode": 400,
                            "errorCode": 1012,
                            "exceptionType": "ValidationException",
                            "message": "1012: Passwords do not match",
                            "error": "Password and password confirmation do not match",
                            "timestamp": "2025-08-24T07:47:24.123456+00:00",
                            "endpoint": "/api/v1/auth/register/",
                            "method": "POST"
                        },
                        "1006: User already exists": {
                            "statusCode": 400,
                            "errorCode": 1006,
                            "exceptionType": "ValidationException",
                            "message": "1006: User already exists",
                            "error": "User with this email or username already exists",
                            "timestamp": "2025-08-24T07:47:24.123456+00:00",
                            "endpoint": "/api/v1/auth/register/",
                            "method": "POST"
                        }
                    }
                }
            )
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
            send_welcome_email(user)
        except Exception as e:
            # Log error but don't interrupt registration
            logger.error(f"Failed to send welcome email to {user.email}: {e}")
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        }, status=status.HTTP_201_CREATED)
    
    def _send_welcome_email(self, user):
        """Отправляет приветственное письмо новому пользователю"""
        try:
            html_message = render_to_string('authentication/welcome_email.html', {
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
            # Логируем ошибку, но не прерываем регистрацию
            logger.error(f"Failed to send welcome email to {user.email}: {e}")


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Login user with username and password",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(
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
                        )
                    }
                )
            ),
            400: ERROR_400_SCHEMA
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_serializer.data
        })


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Refresh access token using refresh token",
        request_body=RefreshSerializer,
        responses={
            200: openapi.Response(
                description="Token refreshed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
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
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_400_BAD_REQUEST)
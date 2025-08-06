from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
import logging

from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode
from .serializers import (
    UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer
)
from .models import User
from .firebase_auth import verify_firebase_token

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class CustomerRegistrationView(BaseAPIView):
    """Customer registration"""
    permission_classes = [AllowAny]
    http_method_names = ['post']
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Customer registration (customer)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Password confirmation'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='US phone number (optional) - Supports: (555) 123-4567, +1 (555) 123-4567, 555-123-4567, 555.123.4567, 555 123 4567, 123-4567, 5551234567'),
                'fcm_token': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase Cloud Messaging token (optional)'),
            },
            example={
                'email': 'shilovscky@i.ua',
                'password': 'shilovscky',
                'confirm_password': 'shilovscky',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone': '(555) 123-4567',
                'fcm_token': 'your-fcm-token-here'
            }
        ),
        responses={
            201: openapi.Response('Successful registration', UserSerializer),
            400: 'Validation error or user already exists'
        },
        tags=['Registration'])
    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'role': 'customer'})
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"Customer registered successfully: {serializer.data.get('email', 'unknown')}")
            return self.success_response(
                data=serializer.data,
                message='Customer registered successfully'
            )
        except Exception as exc:
            logger.error(f"Customer registration failed for email {request.data.get('email', 'unknown')}: {str(exc)}")
            # Позволяем Django обработать стандартные ошибки
            raise

class ProviderRegistrationView(BaseAPIView):
    """Provider registration"""
    permission_classes = [AllowAny]
    http_method_names = ['post']
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Provider registration (provider)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Password confirmation'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='US phone number (optional) - Format: (XXX) XXX-XXXX'),
            },
            example={
                'email': 'shilovscky2020@gmail.com',
                'password': 'shilovscky2020',
                'confirm_password': 'shilovscky2020',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone': '(555) 123-4567'
            }
        ),
        responses={
            201: openapi.Response('Successful registration', UserSerializer),
            400: 'Validation error or user already exists'
        },
        tags=['Registration'])
    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'role': 'provider'})
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"Provider registered successfully: {serializer.data.get('email', 'unknown')}")
            return self.success_response(
                data=serializer.data,
                message='Provider registered successfully'
            )
        except Exception as exc:
            logger.error(f"Provider registration failed for email {request.data.get('email', 'unknown')}: {str(exc)}")
            raise

class ManagementRegistrationView(BaseAPIView):
    """Support Manager registration - for customer support staff"""
    permission_classes = [AllowAny]
    http_method_names = ['post']
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Support Manager registration (support staff)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Password confirmation'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='US phone number (optional) - Supports: (555) 123-4567, +1 (555) 123-4567, 555-123-4567, 555.123.4567, 555 123 4567, 123-4567, 5551234567'),
            },
            example={
                'email': 'cartiuacarti@gmail.com',
                'password': 'cartiuacarti',
                'confirm_password': 'cartiuacarti',
                'first_name': 'Support',
                'last_name': 'Manager',
                'phone': '(555) 123-4567'
            }
        ),
        responses={
            201: openapi.Response('Successful registration', UserSerializer),
            400: 'Validation error or user already exists'
        },
        tags=['Registration'])
    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data, context={'role': 'management'})
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"Management registered successfully: {serializer.data.get('email', 'unknown')}")
            return self.success_response(
                data=serializer.data,
                message='Support Manager registered successfully'
            )
        except Exception as exc:
            logger.error(f"Management registration failed for email {request.data.get('email', 'unknown')}: {str(exc)}")
            raise

class FirebaseAuthView(BaseAPIView):
    """Firebase authentication"""
    permission_classes = [AllowAny]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="Firebase authentication",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id_token', 'provider'],
            properties={
                'id_token': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase ID token'),
                'provider': openapi.Schema(type=openapi.TYPE_STRING, description='Provider (google, facebook, etc.)'),
            },
            example={
                'id_token': 'firebase-id-token-here',
                'provider': 'google'
            }
        ),
        responses={
            200: openapi.Response('Firebase authentication successful'),
            400: 'Invalid token or provider'
        },
        tags=['Firebase Auth'])
    @transaction.atomic
    def post(self, request, provider):
        """Firebase authentication"""
        try:
            id_token = request.data.get('id_token')
            if not id_token:
                return self.error_response(
                    ErrorCode.FIREBASE_INVALID_TOKEN,
                    'Firebase ID token is required'
                )
            
            # Verify Firebase token
            user_info = verify_firebase_token(id_token)
            if not user_info:
                return self.error_response(
                    ErrorCode.FIREBASE_INVALID_TOKEN,
                    'Invalid Firebase token'
                )
            
            # Get or create user
            email = user_info.get('email')
            if not email:
                return self.error_response(
                    ErrorCode.FIREBASE_INVALID_TOKEN,
                    'Email not found in Firebase token'
                )
            
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'role': 'customer',
                    'is_active': True
                }
            )
            
            if created:
                logger.info(f"New user created via Firebase: {email}")
            
            # Generate tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"Firebase authentication successful for user: {email}")
            
            return self.success_response(
                data={
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'role': user.role
                    }
                },
                message='Firebase authentication successful'
            )
            
        except Exception as e:
            logger.error(f"Firebase authentication error: {str(e)}")
            return self.error_response(
                ErrorCode.FIREBASE_SERVICE_UNAVAILABLE,
                f'Firebase authentication error: {str(e)}'
            ) 
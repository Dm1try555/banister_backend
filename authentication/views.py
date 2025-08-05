from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import (
    UserSerializer, RegisterSerializer, ProfileSerializer, 
    EmailConfirmationCodeSerializer, AdminPermissionSerializer,
    AdminUserSerializer, AdminProfileUpdateSerializer, AdminPermissionUpdateSerializer,
    CustomTokenObtainPairSerializer
)
from .firebase_auth import verify_firebase_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, Profile, VerificationCode, EmailConfirmationCode, EmailConfirmationToken, PasswordResetCode, AdminPermission
from file_storage.models import ProfilePhoto, FileStorage  
import random
from rest_framework_simplejwt.tokens import RefreshToken
# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    UserNotFoundError, InvalidCredentialsError, EmailAlreadyExistsError,
    InvalidVerificationCodeError, ExpiredVerificationCodeError, BaseCustomException,
    InvalidEmailError, ValidationError, ServerError)
from error_handling.utils import ErrorResponseMixin, format_validation_errors, create_error_response, create_success_response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
from django.db import IntegrityError
from django.http import Http404
from django.core.cache import cache
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
import logging 



# --- Registration ---
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
            },
            example={
                'email': 'shilovscky@i.ua',
                'password': 'shilovscky',
                'confirm_password': 'shilovscky',
                'first_name': 'John',
                'last_name': 'Doe',
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
            return self.handle_registration_errors(exc)

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
            return self.success_response(
                data=serializer.data,
                message='Provider registered successfully'
            )
        except Exception as exc:
            return self.handle_registration_errors(exc)

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
                'email': 'support@banister.com',
                'password': 'password123',
                'confirm_password': 'password123',
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
            return self.success_response(
                data=serializer.data,
                message='Manager registered successfully'
            )
        except Exception as exc:
            return self.handle_registration_errors(exc)

class FirebaseAuthView(BaseAPIView):
    """Firebase authentication"""
    permission_classes = [AllowAny]
    http_method_names = ['post']

    @transaction.atomic
    def post(self, request, provider):
        id_token = request.data.get('id_token')
        role = request.data.get('role', 'customer')

        if not id_token:
            raise ValidationError('Token not provided')

        decoded_token = verify_firebase_token(id_token)

        email = decoded_token.get('email')
        uid = decoded_token.get('uid')

        if not email:
            raise ValidationError('Invalid token')

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'role': role,
                'password_hash': uid
            }
        )

        if created:
            Profile.objects.create(user=user)
            if user.role == 'provider':
                from providers.models import Provider
                Provider.objects.create(user=user)

        token = CustomTokenObtainPairSerializer.get_token(user)
        return self.success_response(
            data={
                'access': str(token.access_token),
                'refresh': str(token),
                'role': user.role
            },
            message='Successful authentication via Firebase'
        )

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token acquisition"""
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh"""
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Refresh access token using refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            },
            example={
                'refresh': 'your-refresh-token-here'
            }
        ),
        responses={
            200: openapi.Response('Token refreshed successfully', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='New access token'),
                }
            )),
            401: 'Invalid refresh token'
        },
        tags=['Login'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# --- Profile ---
class ProfileView(BaseAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'delete']

    def get_serializer_class(self):
        """Return appropriate serializer based on user role"""
        user = self.request.user
        if user.role == 'provider':
            from .serializers import ProviderUserSerializer
            return ProviderUserSerializer
        elif user.role == 'customer':
            from .serializers import CustomerUserSerializer
            return CustomerUserSerializer
        elif user.role == 'management':
            from .serializers import ManagementUserSerializer
            return ManagementUserSerializer
        else:
            from .serializers import UserSerializer
            return UserSerializer

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        operation_description="Get user profile",
        responses={
            200: openapi.Response('Profile retrieved successfully', UserSerializer),
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Profile'])
    def get(self, request):
        try:
            serializer = self.get_serializer(request.user, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            return self.error_response(
                error_number='SERVER_ERROR',
                error_message=f'Failed to retrieve profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Update user profile (full update) - Role-specific fields. Note: Role cannot be changed.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING, description='Role cannot be changed'),
                'profile': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'bio': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                ),
                'provider_profile': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description='Only available for provider users',
                    properties={
                        'experience_years': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'hourly_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
                    }
                ),
            }
        ),
        responses={
            200: openapi.Response('Profile updated successfully', UserSerializer),
            400: 'Validation error, role change not allowed, or profile photo required for providers/managers',
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Profile'])
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            # Prevent role change
            if 'role' in request.data and request.data['role'] != request.user.role:
                return self.error_response(
                    error_number='ROLE_CHANGE_NOT_ALLOWED',
                    error_message='Changing user role is not allowed',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Get serializer with context for validation
            serializer = self.get_serializer(request.user, data=request.data, context={'request': request})
            if not serializer.is_valid():
                return self.validation_error_response(serializer.errors)
            
            # Check profile photo requirement after validation
            if request.user.role in ['provider', 'management'] and not request.user.has_required_profile_photo():
                return self.error_response(
                    error_number='PROFILE_PHOTO_REQUIRED',
                    error_message='Profile photo is required for providers and managers',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return self.error_response(
                error_number='SERVER_ERROR',
                error_message=f'Failed to update profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


        try:
            # Prevent role change
            if 'role' in request.data and request.data['role'] != request.user.role:
                return self.error_response(
                    error_number='ROLE_CHANGE_NOT_ALLOWED',
                    error_message='Changing user role is not allowed',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Get serializer with context for validation
            serializer = self.get_serializer(request.user, data=request.data, context={'request': request}, partial=True)
            if not serializer.is_valid():
                return self.validation_error_response(serializer.errors)
            
            # Check profile photo requirement after validation
            if request.user.role in ['provider', 'management'] and not request.user.has_required_profile_photo():
                return self.error_response(
                    error_number='PROFILE_PHOTO_REQUIRED',
                    error_message='Profile photo is required for providers and managers',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Update the user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return self.error_response(
                error_number='SERVER_ERROR',
                error_message=f'Failed to partially update profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Delete user account (completely removes user and all associated data)",
        responses={
            204: 'User account deleted successfully',
            400: 'Profile photo required for providers/managers',
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Profile'])
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            if request.user.role in ['provider', 'management'] and not request.user.has_required_profile_photo():
                return self.error_response(
                    error_number='PROFILE_PHOTO_REQUIRED',
                    error_message='Profile photo is required for providers and managers',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the user before deletion for cleanup
            user = request.user
            
            # Delete related objects first
            try:
                # Delete profile if it exists
                if hasattr(user, 'profile'):
                    user.profile.delete()
                
                # Delete provider profile if it exists
                if user.role == 'provider':
                    try:
                        from providers.models import Provider
                        provider = Provider.objects.get(user=user)
                        provider.delete()
                    except Provider.DoesNotExist:
                        pass
                
                # Delete profile photos if they exist
                try:
                    from file_storage.models import ProfilePhoto
                    profile_photos = ProfilePhoto.objects.filter(user=user)
                    for photo in profile_photos:
                        photo.delete()
                except Exception:
                    pass
                
                # Delete verification codes
                VerificationCode.objects.filter(email=user.email).delete()
                
                # Delete email confirmation tokens
                EmailConfirmationToken.objects.filter(email=user.email).delete()
                
                # Delete email confirmation codes
                EmailConfirmationCode.objects.filter(email=user.email).delete()
                
            except Exception as e:
                # Log the error but continue with user deletion
                print(f"Error during cleanup: {e}")
            
            # Finally delete the user
            user.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return self.error_response(
                error_number='SERVER_ERROR',
                error_message=f'Failed to delete user account: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# --- Password Reset ---
@swagger_auto_schema(
    method='post',
    operation_description="Request password reset code. Enter your email to receive a 6-digit reset code.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email address')
        },
        example={
            'email': 'john.doe@example.com'
        }
    ),
    responses={
        200: openapi.Response('Reset code sent', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address')
                    }
                ),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
            }
        )),
        400: 'Email is required',
        404: 'User not found'
    },
    tags=['Password Reset'])
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Request password reset code by email"""
    email = request.data.get('email')
    if not email:
        return Response({
            'success': False,
            'error': {
                'error_number': 'EMAIL_REQUIRED',
                'error_message': 'Email is required',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'error_number': 'USER_NOT_FOUND',
                'error_message': 'User with this email not found',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Generate 6-digit code
    code = str(random.randint(100000, 999999))
    
    # Delete old codes for this user
    PasswordResetCode.objects.filter(email=email).delete()
    
    # Create new reset code
    PasswordResetCode.objects.create(
        email=email,
        code=code
    )
    
    # Send reset email
    subject = 'Password Reset Code'
    message = f'''
    Hello!
    
    You requested a password reset for your account.
    Your reset code is: {code}
    
    This code is valid for 10 minutes.
    
    If you did not request this reset, please ignore this email.
    '''
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email]
        )
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'error_number': 'EMAIL_SEND_ERROR',
                'error_message': 'Failed to send reset email',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': True,
        'data': {'email': email},
        'message': 'Password reset code sent to your email'
    }, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_description="Reset password using code from email. Enter the 6-digit code and your new password.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'code', 'new_password'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email address'),
            'code': openapi.Schema(type=openapi.TYPE_STRING, description='6-digit reset code from email'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password (min 8 characters)')
        },
        example={
            'email': 'john.doe@example.com',
            'code': '123456',
            'new_password': 'MyNewSecurePassword123!'
        }
    ),
    responses={
        200: openapi.Response('Password reset successful', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'data': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email')
                    }
                ),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
            }
        )),
        400: 'Invalid code, expired code, or weak password',
        404: 'Code not found'
    },
    tags=['Password Reset'])
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset using code"""
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    
    if not all([email, code, new_password]):
        return Response({
            'success': False,
            'error': {
                'error_number': 'MISSING_FIELDS',
                'error_message': 'Email, code, and new_password are required',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate password strength
    if len(new_password) < 8:
        return Response({
            'success': False,
            'error': {
                'error_number': 'WEAK_PASSWORD',
                'error_message': 'Password must be at least 8 characters long',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        reset_code = PasswordResetCode.objects.get(email=email, code=code, is_used=False)
    except PasswordResetCode.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'error_number': 'INVALID_CODE',
                'error_message': 'Invalid or used reset code',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    if reset_code.is_expired():
        return Response({
            'success': False,
            'error': {
                'error_number': 'EXPIRED_CODE',
                'error_message': 'Reset code has expired',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'error_number': 'USER_NOT_FOUND',
                'error_message': 'User not found',
                'timestamp': timezone.now().isoformat()
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Update password
    user.set_password(new_password)
    user.save()
    
    # Mark code as used
    reset_code.is_used = True
    reset_code.save()
    
    return Response({
        'success': True,
        'data': {'email': user.email},
        'message': 'Password reset successful'
    }, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    operation_description="User logout - Clears authentication token from Swagger UI",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={},
        description="No body required - just click Execute to logout"
    ),
    responses={
        200: openapi.Response('Logout successful', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'instructions': openapi.Schema(type=openapi.TYPE_STRING, description='Instructions for clearing token in Swagger UI')
            }
        )),
        401: 'Authentication required'
    },
        tags=['Login'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    return Response({
        'success': True, 
        'message': 'Logout successful',
        'instructions': 'To complete logout, please clear the Authorization field in Swagger UI by clicking the "Authorize" button and then "Logout" or manually clear the Bearer token.'
    })

class VerificationCodeSenderMixin:
    """Mixin for sending confirmation code by email or phone"""
    serializer_class = None
    user_check_required = False
    def send_code(self, email, phone):
        code = str(random.randint(100000, 999999))
        VerificationCode.objects.create(email=email, phone=phone, code=code)
        # Placeholder for email/SMS sending (implement in production)
        return code
    @transaction.atomic
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)

            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')

            if self.user_check_required:
                if not User.objects.filter(email=email).exists() and not User.objects.filter(phone=phone).exists():
                    raise UserNotFoundError('User not found')

            code = self.send_code(email, phone)

            return self.success_response(
                data={'code': code},  # Remove in production
                message='Confirmation code sent'
            )
        except BaseCustomException as e:
            raise
        except Exception as e:
            return self.error_response(
                error_number='CODE_SEND_ERROR',
                error_message=f'Error sending code: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerificationCodeVerifyMixin:
    """Mixin for verifying confirmation code and issuing token"""
    serializer_class = None
    create_user_if_not_exists = False
    def verify_code(self, email, phone, code):
        try:
            vcode = VerificationCode.objects.filter(
                email=email,
                phone=phone,
                code=code,
                is_used=False
            ).latest('created_at')

            if vcode.created_at < timezone.now() - timedelta(minutes=10):
                raise ExpiredVerificationCodeError('Confirmation code expired')

            vcode.is_used = True
            vcode.save()
            return vcode
        except VerificationCode.DoesNotExist:
            raise InvalidVerificationCodeError('Invalid confirmation code')
    @transaction.atomic
    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)

            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            code = serializer.validated_data.get('code')

            vcode = self.verify_code(email, phone, code)

            if self.create_user_if_not_exists:
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': email.split('@')[0] if email else f'user_{phone}',
                        'role': 'customer'
                    }
                )
                if created:
                    Profile.objects.create(user=user)
            else:
                user = User.objects.get(email=email) if email else User.objects.get(phone=phone)

            token = CustomTokenObtainPairSerializer.get_token(user)

            return self.success_response(
                data={
                    'access': str(token.access_token),
                    'refresh': str(token),
                    'role': user.role
                },
                message='Successful verification'
            )
        except BaseCustomException as e:
            raise
        except Exception as e:
            return self.error_response(
                error_number='VERIFICATION_ERROR',
                error_message=f'Verification error: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomerLoginView(TokenObtainPairView):
    """Customer login"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Customer authentication (customer)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            example={
                'email': 'shilovscky@i.ua',
                'password': 'shilovscky'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Check if user has customer role
                user = User.objects.get(email=request.data.get('email'))
                if user.role != 'customer':
                    return create_error_response(
                        error_number='ROLE_MISMATCH',
                        error_message='This login is for customers only',
                        status_code=401
                    )
                
                return create_success_response(
                    data=response.data,
                    message='Customer login successful'
                )
            else:
                return create_error_response(
                    error_number='AUTHENTICATION_ERROR',
                    error_message='Invalid email or password',
                    status_code=401
                )
                
        except User.DoesNotExist:
            return create_error_response(
                error_number='AUTHENTICATION_ERROR',
                error_message='Invalid email or password',
                status_code=401
            )
        except Exception as e:
            return create_error_response(
                error_number='AUTHENTICATION_ERROR',
                error_message='Invalid email or password',
                status_code=401
            )

class ProviderLoginView(TokenObtainPairView):
    """Provider login"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Provider authentication (provider)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            example={
                'email': 'shilovscky2020@gmail.com',
                'password': 'shilovscky2020'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Check if user has provider role
                user = User.objects.get(email=request.data.get('email'))
                if user.role != 'provider':
                    return create_error_response(
                        error_number='ROLE_MISMATCH',
                        error_message='This login is for providers only',
                        status_code=401
                    )
                
                return create_success_response(
                    data=response.data,
                    message='Provider login successful'
                )
            else:
                return create_error_response(
                    error_number='AUTHENTICATION_ERROR',
                    error_message='Invalid email or password',
                    status_code=401
                )
                
        except User.DoesNotExist:
            return create_error_response(
                error_number='AUTHENTICATION_ERROR',
                error_message='Invalid email or password',
                status_code=401
            )
        except Exception as e:
            return create_error_response(
                error_number='AUTHENTICATION_ERROR',
                error_message='Invalid email or password',
                status_code=401
            )

class ManagementLoginView(TokenObtainPairView):
    """Support Manager login - for customer support staff"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Support Manager authentication (support staff)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            example={
                'email': 'support@banister.com',
                'password': 'password123'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Check if user has management role
                user = User.objects.get(email=request.data.get('email'))
                if user.role != 'management':
                    return create_error_response(
                        error_number='ROLE_MISMATCH',
                        error_message='This login is for management staff only',
                        status_code=401
                    )
                
                return create_success_response(
                    data=response.data,
                    message='Management login successful'
                )
            else:
                return create_error_response(
                    error_number='AUTHENTICATION_ERROR',
                    error_message='Invalid email or password',
                    status_code=401
                )
                
        except User.DoesNotExist:
            return create_error_response(
                error_number='AUTHENTICATION_ERROR',
                error_message='Invalid email or password',
                status_code=401
            )
        except Exception as e:
            return create_error_response(
                error_number='AUTHENTICATION_ERROR',
                error_message='Invalid email or password',
                status_code=401
            )

class AdminLoginView(TokenObtainPairView):
    """Admin login - only for admin role"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Admin authentication (admin role only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            example={
                'email': 'admin@banister.com',
                'password': 'password123'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    def post(self, request, *args, **kwargs):
        try:
            # Validate credentials
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = serializer.user
            
            # Check if user has admin role
            if user.role != 'admin':
                logger.warning(f"Login attempt for non-admin user: {user.email} (role: {user.role})")
                return Response(
                    {'error': 'Access denied. This endpoint is for admin users only.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Add role to token
            access_token['role'] = user.role
            
            logger.info(f"Admin login successful: {user.email}")
            return Response({
                'access': str(access_token),
                'refresh': str(refresh),
                'role': user.role
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Admin login failed: {str(exc)}")
            return Response(
                {'error': 'Invalid credentials or access denied'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class SuperAdminLoginView(TokenObtainPairView):
    """Super Admin login - only for super_admin role"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Super Admin authentication (super_admin role only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            example={
                'email': 'superadmin@banister.com',
                'password': 'AdminPass123!'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    def post(self, request, *args, **kwargs):
        try:
            # Validate credentials
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = serializer.user
            
            # Check if user has super_admin role
            if user.role != 'super_admin':
                logger.warning(f"Login attempt for non-super-admin user: {user.email} (role: {user.role})")
                return Response(
                    {'error': 'Access denied. This endpoint is for super admin users only.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Add role to token
            access_token['role'] = user.role
            
            logger.info(f"Super Admin login successful: {user.email}")
            return Response({
                'access': str(access_token),
                'refresh': str(refresh),
                'role': user.role
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Super Admin login failed: {str(exc)}")
            return Response(
                {'error': 'Invalid credentials or access denied'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class AccountantLoginView(TokenObtainPairView):
    """Accountant login - only for accountant role"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Accountant authentication (accountant role only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            example={
                'email': 'accountant@banister.com',
                'password': 'password123'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    def post(self, request, *args, **kwargs):
        try:
            # Validate credentials
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = serializer.user
            
            # Check if user has accountant role
            if user.role != 'accountant':
                logger.warning(f"Login attempt for non-accountant user: {user.email} (role: {user.role})")
                return Response(
                    {'error': 'Access denied. This endpoint is for accountant users only.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Add role to token
            access_token['role'] = user.role
            
            logger.info(f"Accountant login successful: {user.email}")
            return Response({
                'access': str(access_token),
                'refresh': str(refresh),
                'role': user.role
            }, status=status.HTTP_200_OK)
            
        except Exception as exc:
            logger.error(f"Accountant login failed: {str(exc)}")
            return Response(
                {'error': 'Invalid credentials or access denied'},
                status=status.HTTP_401_UNAUTHORIZED
            )


@swagger_auto_schema(
    method='post',
    operation_description="Request email confirmation link. Enter your email to receive a confirmation link.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Email address for confirmation')
        },
        example={
            'email': 'john.doe@example.com'
        }
    ),
    responses={
        200: openapi.Response('Link sent', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
            }
        )),
        400: 'Error: email is required'
    },
    tags=['Email confirmation'])
@api_view(['POST'])
@permission_classes([AllowAny])
def email_confirm_request(request):
    """Send email confirmation link"""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=400)

    token = str(uuid.uuid4())
    expires_at = timezone.now() + timedelta(hours=24)

    EmailConfirmationToken.objects.filter(email=email).delete()
    EmailConfirmationToken.objects.create(email=email, token=token, expires_at=expires_at)

    confirmation_url = f"{settings.FRONTEND_URL}/confirm-email?token={token}"
    subject = 'Email confirmation'
    message = f'''
    Hello!

    To confirm your email, please click the link:
    {confirmation_url}

    This link is valid for 24 hours.

    If you did not register on our website, please ignore this email.
    '''

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email]
    )

    return Response({'success': True, 'message': 'Email confirmation link sent'}, status=200)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'token',
            openapi.IN_QUERY,
            description='Email confirmation token from link',
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Email confirmed', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )),
        400: 'Error: token is required, invalid or expired token'
    },
    tags=['Email confirmation'])
@api_view(['GET'])
@permission_classes([AllowAny])
def email_confirm_verify(request):
    """Verify email by token from link"""
    token = request.GET.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=400)

    try:
        confirmation = EmailConfirmationToken.objects.get(token=token, is_used=False)
    except EmailConfirmationToken.DoesNotExist:
        return Response({'error': 'Invalid or used token'}, status=400)

    if confirmation.is_expired():
        return Response({'error': 'Token expired'}, status=400)

    confirmation.is_used = True
    confirmation.save()

    try:
        user = User.objects.get(email=confirmation.email)
        profile = Profile.objects.get(user=user)
        profile.is_email_confirmed = True
        profile.save()
    except (User.DoesNotExist, Profile.DoesNotExist):
        pass

    return Response({'success': True, 'message': 'Email confirmed successfully'}, status=200)

# Удаляем устаревший ProfilePhotoView, так как теперь используется система из file_storage

class AdminProfileUpdateView(BaseAPIView):
    """Update admin profile data (first_name, last_name)"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['put']

    @swagger_auto_schema(
        operation_description="Update admin profile data (first_name, last_name)",
        request_body=AdminProfileUpdateSerializer,
        responses={
            200: openapi.Response('Profile updated successfully', AdminProfileUpdateSerializer),
            400: 'Validation error',
            403: 'Access denied - only admin users can update their profile',
            404: 'Profile not found',
            500: 'Server error'
        },
        tags=['Admin'])
    def put(self, request):
        try:
            # Check if user is admin
            if not request.user.is_admin_role():
                return create_error_response(
                    error_number='ACCESS_DENIED',
                    error_message='Access denied. Only admin users can update their profile.',
                    status_code=403
                )

            # Get user profile
            try:
                profile = request.user.profile
            except Profile.DoesNotExist:
                return create_error_response(
                    error_number='PROFILE_NOT_FOUND',
                    error_message='Profile not found for this user.',
                    status_code=404
                )

            # Validate and update profile
            serializer = AdminProfileUpdateSerializer(profile, data=request.data, partial=True)
            if not serializer.is_valid():
                return create_error_response(
                    error_number='VALIDATION_ERROR',
                    error_message='Invalid data provided.',
                    status_code=400
                )

            serializer.save()

            return create_success_response(
                data=serializer.data,
                message='Admin profile updated successfully'
            )

        except Exception as e:
            return create_error_response(
                error_number='SERVER_ERROR',
                error_message=f'Server error occurred: {str(e)}',
                status_code=500
            )


class AdminPermissionManagementView(BaseAPIView):
    """Manage admin permissions (grant/revoke) - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'get', 'delete']

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
    def post(self, request):
        """Grant permissions to admin user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                logger.warning(f"Permission management attempt by non-super-admin: {request.user.email}")
                return self.error_response(
                    message='Access denied. Only super admin can manage permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            serializer = AdminPermissionUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return self.error_response(
                    message='Validation error',
                    data=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            admin_user_id = serializer.validated_data['admin_user_id']
            permissions = serializer.validated_data['permissions']
            action = serializer.validated_data['action']

            # Get admin user
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    message='Admin user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )

            # Validate permissions
            valid_permissions = [choice[0] for choice in AdminPermission.PERMISSION_CHOICES]
            invalid_permissions = [p for p in permissions if p not in valid_permissions]
            if invalid_permissions:
                return self.error_response(
                    message=f'Invalid permissions: {", ".join(invalid_permissions)}',
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Process permissions
            with transaction.atomic():
                if action == 'grant':
                    for permission in permissions:
                        AdminPermission.objects.get_or_create(
                            admin_user=admin_user,
                            permission=permission,
                            defaults={
                                'is_active': True,
                                'granted_by': request.user
                            }
                        )
                    message = f'Permissions granted successfully to {admin_user.email}'
                elif action == 'revoke':
                    AdminPermission.objects.filter(
                        admin_user=admin_user,
                        permission__in=permissions
                    ).update(is_active=False)
                    message = f'Permissions revoked successfully from {admin_user.email}'
                else:
                    return self.error_response(
                        message='Invalid action. Use "grant" or "revoke"',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            
            logger.info(f"Permissions {action}ed for admin {admin_user.email} by super admin {request.user.email}")
            return self.success_response(
                data={'admin_user_id': admin_user_id, 'permissions': permissions, 'action': action},
                message=message
            )
            
        except Exception as exc:
            logger.error(f"Permission management error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while managing permissions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        """Get permissions for specific admin user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                return self.error_response(
                    message='Access denied. Only super admin can view permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            admin_user_id = request.query_params.get('admin_user_id')
            if not admin_user_id:
                return self.error_response(
                    message='admin_user_id parameter is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    message='Admin user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            permissions = AdminPermission.objects.filter(admin_user=admin_user)
            serializer = AdminPermissionSerializer(permissions, many=True)
            
            return self.success_response(
                data={
                    'admin_user': {
                        'id': admin_user.id,
                        'email': admin_user.email,
                        'role': admin_user.role
                    },
                    'permissions': serializer.data
                },
                message='Admin permissions retrieved successfully'
            )
            
        except Exception as exc:
            logger.error(f"Get permissions error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while retrieving permissions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
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
    def delete(self, request):
        """Delete specific permission for admin user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                return self.error_response(
                    message='Access denied. Only super admin can delete permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            admin_user_id = request.data.get('admin_user_id')
            permission = request.data.get('permission')
            
            if not admin_user_id or not permission:
                return self.error_response(
                    message='admin_user_id and permission are required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    message='Admin user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            try:
                admin_permission = AdminPermission.objects.get(
                                admin_user=admin_user,
                    permission=permission
                )
                admin_permission.delete()
                
                logger.info(f"Permission {permission} deleted for admin {admin_user.email} by super admin {request.user.email}")
                return self.success_response(
                    message=f'Permission {permission} deleted successfully for {admin_user.email}'
                )
                
            except AdminPermission.DoesNotExist:
                return self.error_response(
                    message='Permission not found for this admin user',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
        except Exception as exc:
            logger.error(f"Delete permission error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while deleting permission',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class AdminPermissionDetailView(BaseAPIView):
    """Detailed admin permission management - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']

    @swagger_auto_schema(
        operation_description="Get all admin users with their permissions (Super Admin only)",
        responses={
            200: openapi.Response('Admin users with permissions', AdminUserSerializer),
            403: 'Access denied - only super admin can view admin list',
            500: 'Server error'
        },
        tags=['Admin'])
    def get(self, request):
        """Get all admin users with their permissions"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                return self.error_response(
                    error_number='ACCESS_DENIED',
                    error_message='Access denied. Only super admin can view admin list.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Get only admin users (role='admin')
            admin_users = User.objects.filter(role='admin')
            
            # Prepare response data with permissions
            admin_users_data = []
            for user in admin_users:
                user_data = AdminUserSerializer(user).data
                # Get user permissions
                user_permissions = AdminPermission.objects.filter(admin_user=user, is_active=True).values_list('permission', flat=True)
                user_data['permissions'] = list(user_permissions)
                admin_users_data.append(user_data)
            
            return self.success_response(
                data={'admin_users': admin_users_data},
                message='Admin users with permissions retrieved successfully'
            )
            
        except Exception as exc:
            logger.error(f"Get admin list error: {str(exc)}")
            return self.error_response(
                error_number='SERVER_ERROR',
                error_message='Server error occurred while retrieving admin list',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Bulk update permissions for admin users (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['updates'],
            properties={
                'updates': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'admin_user_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'permissions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                            'action': openapi.Schema(type=openapi.TYPE_STRING, enum=['grant', 'revoke'])
                        }
                    )
                )
            }
        ),
        responses={
            200: openapi.Response('Permissions updated successfully'),
            400: 'Validation error',
            403: 'Access denied - only super admin can manage permissions',
            500: 'Server error'
        },
        tags=['Admin'])
    def post(self, request):
        """Bulk update permissions for multiple admin users"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                return self.error_response(
                    error_number='ACCESS_DENIED',
                    error_message='Access denied. Only super admin can manage permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            updates = request.data.get('updates', [])
            if not updates:
                return self.error_response(
                    error_number='MISSING_FIELD',
                    error_message='Updates array is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            results = []
            with transaction.atomic():
                for update in updates:
                    admin_user_id = update.get('admin_user_id')
                    permissions = update.get('permissions', [])
                    action = update.get('action')
                    
                    if not all([admin_user_id, permissions, action]):
                        return self.error_response(
                            error_number='MISSING_FIELD',
                            error_message='Each update must contain admin_user_id, permissions, and action',
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
                    
                    if action not in ['grant', 'revoke']:
                        return self.error_response(
                            error_number='INVALID_ACTION',
                            error_message='Action must be "grant" or "revoke"',
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
                    
                    try:
                        admin_user = User.objects.get(id=admin_user_id, role='admin')
                    except User.DoesNotExist:
                        results.append({
                            'admin_user_id': admin_user_id,
                            'status': 'error',
                            'message': 'Admin user not found'
                        })
                        continue
                    
                    # Validate permissions
                    valid_permissions = [choice[0] for choice in AdminPermission.PERMISSION_CHOICES]
                    invalid_permissions = [p for p in permissions if p not in valid_permissions]
                    if invalid_permissions:
                        results.append({
                            'admin_user_id': admin_user_id,
                            'status': 'error',
                            'message': f'Invalid permissions: {", ".join(invalid_permissions)}'
                        })
                        continue
                    
                    # Process permissions
                    if action == 'grant':
                        for permission in permissions:
                            AdminPermission.objects.get_or_create(
                                admin_user=admin_user,
                                permission=permission,
                                defaults={
                                    'is_active': True,
                                    'granted_by': request.user
                                }
                            )
                    elif action == 'revoke':
                        AdminPermission.objects.filter(
                            admin_user=admin_user,
                            permission__in=permissions
                        ).update(is_active=False)
                    
                    results.append({
                    'admin_user_id': admin_user_id,
                    'admin_user_email': admin_user.email,
                        'status': 'success',
                    'action': action,
                        'permissions': permissions
                    })
            
            logger.info(f"Bulk permission update by super admin {request.user.email}: {len(results)} updates")
            return self.success_response(
                data={'results': results},
                message='Bulk permission update completed'
            )
            
        except Exception as exc:
            logger.error(f"Bulk permission update error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while updating permissions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Check if admin user has specific permissions (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['admin_user_id', 'permissions'],
            properties={
                'admin_user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Admin user ID'),
                'permissions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='Permissions to check'),
            }
        ),
        responses={
            200: openapi.Response('Permission check results'),
            400: 'Validation error',
            403: 'Access denied - only super admin can check permissions',
            404: 'Admin user not found',
            500: 'Server error'
        },
        tags=['Admin'])
    def put(self, request):
        """Check if admin user has specific permissions"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                return self.error_response(
                    error_number='ACCESS_DENIED',
                    error_message='Access denied. Only super admin can check permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            admin_user_id = request.data.get('admin_user_id')
            permissions = request.data.get('permissions', [])
            
            if not admin_user_id or not permissions:
                return self.error_response(
                    error_number='MISSING_FIELD',
                    error_message='admin_user_id and permissions are required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    error_number='USER_NOT_FOUND',
                    error_message='Admin user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Check permissions
            user_permissions = AdminPermission.objects.filter(
                admin_user=admin_user,
                is_active=True
            ).values_list('permission', flat=True)
            
            permission_status = {}
            for permission in permissions:
                permission_status[permission] = permission in user_permissions
            
            return self.success_response(
                data={
                    'admin_user': {
                        'id': admin_user.id,
                        'email': admin_user.email,
                        'role': admin_user.role
                    },
                    'permission_status': permission_status,
                    'all_permissions': list(user_permissions)
                },
                message='Permission check completed successfully'
            )
            
        except Exception as exc:
            logger.error(f"Permission check error: {str(exc)}")
            return self.error_response(
                error_number='SERVER_ERROR',
                error_message='Server error occurred while checking permissions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Reset all permissions for admin user (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['admin_user_id'],
            properties={
                'admin_user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Admin user ID'),
            }
        ),
        responses={
            200: openapi.Response('Permissions reset successfully'),
            400: 'Validation error',
            403: 'Access denied - only super admin can reset permissions',
            404: 'Admin user not found',
            500: 'Server error'
        },
        tags=['Admin'])
    def delete(self, request):
        """Reset all permissions for admin user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                return self.error_response(
                    error_number='ACCESS_DENIED',
                    error_message='Access denied. Only super admin can reset permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            admin_user_id = request.data.get('admin_user_id')
            if not admin_user_id:
                return self.error_response(
                    error_number='MISSING_FIELD',
                    error_message='admin_user_id is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    error_number='USER_NOT_FOUND',
                    error_message='Admin user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Delete all permissions for this admin user
            deleted_count = AdminPermission.objects.filter(admin_user=admin_user).delete()[0]
            
            logger.info(f"All permissions reset for admin {admin_user.email} by super admin {request.user.email}")
            return self.success_response(
                data={'deleted_permissions_count': deleted_count},
                message=f'All permissions reset successfully for {admin_user.email}'
            )
            
        except Exception as exc:
            logger.error(f"Reset permissions error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while resetting permissions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )






class CreateAdminView(BaseAPIView):
    """Create admin user via API - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="Create admin user (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Password confirmation'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number (optional)'),
                'permissions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING), description='Permissions (optional)'),
            },
            example={
                'email': 'admin@example.com',
                'password': 'securepass123',
                'confirm_password': 'securepass123',
                'first_name': 'Admin',
                'last_name': 'User',
                'phone': '(555) 123-4567',
                'permissions': ['user_management', 'service_management']
            }
        ),
        responses={
            201: openapi.Response('Admin user created successfully', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'phone': openapi.Schema(type=openapi.TYPE_STRING),
                            'role': openapi.Schema(type=openapi.TYPE_STRING),
                            'profile': openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'bio': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            ),
                            'provider_profile': openapi.Schema(type=openapi.TYPE_OBJECT, nullable=True),
                            'profile_photo_url': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
                            'has_required_profile_photo': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'permissions': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING),
                                description='List of granted permissions'
                            )
                        }
                    )
                }
            )),
            400: 'Validation error or user already exists',
            403: 'Access denied - only super admin can create admin users',
            500: 'Server error'
        },
        tags=['Admin'])
    def post(self, request):
        """Create admin user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                logger.warning(f"Admin creation attempt by non-super-admin: {request.user.email}")
                return self.error_response(
                    error_number='ACCESS_DENIED',
                    error_message='Access denied. Only super admin can create admin users.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            # Validate required fields
            required_fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name']
            for field in required_fields:
                if not request.data.get(field):
                    return self.error_response(
                        error_number='MISSING_FIELD',
                        error_message=f'{field} is required',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            email = request.data.get('email')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            phone = request.data.get('phone', '')
            permissions = request.data.get('permissions', [])
            # Validate password confirmation
            if password != confirm_password:
                return self.error_response(
                    error_number='PASSWORD_MISMATCH',
                    error_message='Password and confirm_password must match',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            # Validate password strength
            if len(password) < 8:
                return self.error_response(
                    error_number='WEAK_PASSWORD',
                    error_message='Password must be at least 8 characters long',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return self.error_response(
                    error_number='USER_EXISTS',
                    error_message='User with this email already exists',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            # Validate permissions
            if permissions:
                valid_permissions = [choice[0] for choice in AdminPermission.PERMISSION_CHOICES]
                invalid_permissions = [p for p in permissions if p not in valid_permissions]
                if invalid_permissions:
                    return self.error_response(
                        error_number='INVALID_PERMISSION',
                        error_message=f'Invalid permissions: {", ".join(invalid_permissions)}',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            with transaction.atomic():
                # Create user with admin role
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    role='admin',
                    phone=phone,
                    is_staff=True,
                    is_superuser=False
                )
                # Create profile
                Profile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name
                )
                # Grant permissions
                for permission in permissions:
                    AdminPermission.objects.create(
                        admin_user=user,
                        permission=permission,
                        is_active=True,
                        granted_by=request.user
                    )
                # Get user permissions
                user_permissions = AdminPermission.objects.filter(admin_user=user, is_active=True).values_list('permission', flat=True)
                # Serialize response
                serializer = UserSerializer(user)
                response_data = serializer.data
                response_data['permissions'] = list(user_permissions)
                logger.info(f"Admin user created by super admin {request.user.email}: {email}")
                return self.success_response(
                    data=response_data,
                    message='Admin user created successfully'
                )
        except Exception as exc:
            logger.error(f"Admin user creation error: {str(exc)}")
            return self.error_response(
                error_number='SERVER_ERROR',
                error_message='Server error occurred while creating admin user',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateAccountantView(BaseAPIView):
    """Create accountant user via API - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="Create accountant user (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Password confirmation'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number (optional)'),
            },
            example={
                'email': 'accountant@example.com',
                'password': 'securepass123',
                'confirm_password': 'securepass123',
                'first_name': 'Accountant',
                'last_name': 'User',
                'phone': '(555) 123-4567'
            }
        ),
        responses={
            201: openapi.Response('Accountant user created successfully', UserSerializer),
            400: 'Validation error or user already exists',
            403: 'Access denied - only super admin can create accountant users',
            500: 'Server error'
        },
        tags=['Accountant'])
    def post(self, request):
        """Create accountant user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                logger.warning(f"Accountant creation attempt by non-super-admin: {request.user.email}")
                return self.error_response(
                    message='Access denied. Only super admin can create accountant users.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Validate required fields
            required_fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name']
            for field in required_fields:
                if not request.data.get(field):
                    return self.error_response(
                        message=f'{field} is required',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            
            email = request.data.get('email')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            phone = request.data.get('phone', '')
            
            # Validate password confirmation
            if password != confirm_password:
                return self.error_response(
                    message='Password and confirm_password must match',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate password strength
            if len(password) < 8:
                return self.error_response(
                    message='Password must be at least 8 characters long',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return self.error_response(
                    message='User with this email already exists',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # Create user with accountant role
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    role='accountant',
                    phone=phone,
                    is_staff=True,
                    is_superuser=False
                )
                
                # Create profile
                Profile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Grant default financial permissions
                accountant_permissions = [
                    'payment_management',
                    'withdrawal_management',
                    'financial_reports',
                    'document_management'
                ]
                for permission in accountant_permissions:
                    AdminPermission.objects.create(
                        admin_user=user,
                        permission=permission,
                        is_active=True,
                        granted_by=request.user
                    )
                
                # Serialize response
                serializer = UserSerializer(user)
                
                logger.info(f"Accountant user created by super admin {request.user.email}: {email}")
                return self.success_response(
                    data=serializer.data,
                    message='Accountant user created successfully'
                )
                
        except Exception as exc:
            logger.error(f"Accountant user creation error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while creating accountant user',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateSupportManagerView(BaseAPIView):
    """Create support manager user via API - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="Create support manager user (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'confirm_password', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Password confirmation'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number (optional)'),
            },
            example={
                'email': 'support@example.com',
                'password': 'securepass123',
                'confirm_password': 'securepass123',
                'first_name': 'Support',
                'last_name': 'Manager',
                'phone': '(555) 123-4567'
            }
        ),
        responses={
            201: openapi.Response('Support manager created successfully', UserSerializer),
            400: 'Validation error or user already exists',
            403: 'Access denied - only super admin can create support manager users',
            500: 'Server error'
        },
        tags=['Support Manager'])
    def post(self, request):
        """Create support manager user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                logger.warning(f"Support manager creation attempt by non-super-admin: {request.user.email}")
                return self.error_response(
                    message='Access denied. Only super admin can create support manager users.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # Validate required fields
            required_fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name']
            for field in required_fields:
                if not request.data.get(field):
                    return self.error_response(
                        message=f'{field} is required',
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
            
            email = request.data.get('email')
            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            phone = request.data.get('phone', '')
            
            # Validate password confirmation
            if password != confirm_password:
                return self.error_response(
                    message='Password and confirm_password must match',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate password strength
            if len(password) < 8:
                return self.error_response(
                    message='Password must be at least 8 characters long',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return self.error_response(
                    message='User with this email already exists',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            with transaction.atomic():
                # Create user with management role
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    role='management',
                    phone=phone,
                    is_staff=True,
                    is_superuser=False
                )
                
                # Create profile
                Profile.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Serialize response
                serializer = UserSerializer(user)
                
                logger.info(f"Support manager created by super admin {request.user.email}: {email}")
                return self.success_response(
                    data=serializer.data,
                    message='Support manager created successfully'
                )
                
        except Exception as exc:
            logger.error(f"Support manager creation error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while creating support manager user',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class AccountantCRUDView(BaseAPIView):
    """CRUD operations for Accountant users - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'delete']

    @swagger_auto_schema(
        operation_description="List all accountant users (Super Admin only)",
        responses={
            200: openapi.Response('Accountant users list', AdminUserSerializer),
            403: 'Access denied - only super admin can view accountant list',
            500: 'Server error'
        },
        tags=['Accountant'])
    def get(self, request):
        """List all accountant users"""
        try:
            if not request.user.is_super_admin():
                return self.error_response(
                    message='Access denied. Only super admin can view accountant list.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            accountants = User.objects.filter(role='accountant')
            serializer = AdminUserSerializer(accountants, many=True)
            
            return self.success_response(
                data={'accountants': serializer.data},
                message='Accountant users list retrieved successfully'
            )
            
        except Exception as exc:
            logger.error(f"Get accountant list error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while retrieving accountant list',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Update accountant user (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID to update'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='User active status'),
            }
        ),
        responses={
            200: openapi.Response('Accountant user updated successfully', UserSerializer),
            400: 'Validation error',
            403: 'Access denied - only super admin can update accountant users',
            404: 'User not found',
            500: 'Server error'
        },
        tags=['Accountant'])
    def put(self, request):
        """Update accountant user"""
        try:
            if not request.user.is_super_admin():
                return self.error_response(
                    message='Access denied. Only super admin can update accountant users.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            user_id = request.data.get('user_id')
            is_active = request.data.get('is_active')
            
            if not user_id:
                return self.error_response(
                    message='user_id is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(id=user_id, role='accountant')
            except User.DoesNotExist:
                return self.error_response(
                    message='Accountant user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            if is_active is not None:
                user.is_active = is_active
                user.save()
            
            serializer = UserSerializer(user)
            logger.info(f"Accountant user updated by super admin {request.user.email}: {user.email}")
            return self.success_response(
                    data=serializer.data,
                message='Accountant user updated successfully'
            )
            
        except Exception as exc:
            logger.error(f"Accountant user update error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while updating accountant user',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Delete accountant user (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id'],
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID to delete'),
            }
        ),
        responses={
            200: openapi.Response('Accountant user deleted successfully'),
            400: 'Validation error',
            403: 'Access denied - only super admin can delete accountant users',
            404: 'User not found',
            500: 'Server error'
        },
        tags=['Accountant'])
    def delete(self, request):
        """Delete accountant user"""
        try:
            if not request.user.is_super_admin():
                return self.error_response(
                    message='Access denied. Only super admin can delete accountant users.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            user_id = request.data.get('user_id')
            
            if not user_id:
                return self.error_response(
                    message='user_id is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(id=user_id, role='accountant')
            except User.DoesNotExist:
                return self.error_response(
                    message='Accountant user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            if user.id == request.user.id:
                return self.error_response(
                    message='Cannot delete your own account',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            user_email = user.email
            user.delete()
            
            logger.info(f"Accountant user deleted by super admin {request.user.email}: {user_email}")
            return self.success_response(
                message=f'Accountant user {user_email} deleted successfully'
            )
            
        except Exception as exc:
            logger.error(f"Accountant user deletion error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while deleting accountant user',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SupportManagerCRUDView(BaseAPIView):
    """CRUD operations for Support Manager users - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'delete']

    @swagger_auto_schema(
        operation_description="List all support manager users (Super Admin only)",
        responses={
            200: openapi.Response('Support manager users list', AdminUserSerializer),
            403: 'Access denied - only super admin can view support manager list',
            500: 'Server error'
        },
        tags=['Support Manager'])
    def get(self, request):
        """List all support manager users"""
        try:
            if not request.user.is_super_admin():
                return self.error_response(
                    message='Access denied. Only super admin can view support manager list.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            support_managers = User.objects.filter(role='management')
            serializer = AdminUserSerializer(support_managers, many=True)
            
            return self.success_response(
                data={'support_managers': serializer.data},
                message='Support manager users list retrieved successfully'
            )
            
        except Exception as exc:
            logger.error(f"Get support manager list error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while retrieving support manager list',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Update support manager user (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID to update'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='User active status'),
            }
        ),
        responses={
            200: openapi.Response('Support manager user updated successfully', UserSerializer),
            400: 'Validation error',
            403: 'Access denied - only super admin can update support manager users',
            404: 'User not found',
            500: 'Server error'
        },
        tags=['Support Manager'])
    def put(self, request):
        """Update support manager user"""
        try:
            if not request.user.is_super_admin():
                return self.error_response(
                    message='Access denied. Only super admin can update support manager users.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            user_id = request.data.get('user_id')
            is_active = request.data.get('is_active')
            
            if not user_id:
                return self.error_response(
                    message='user_id is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(id=user_id, role='management')
            except User.DoesNotExist:
                return self.error_response(
                    message='Support manager user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            if is_active is not None:
                user.is_active = is_active
                user.save()
            
            serializer = UserSerializer(user)
            logger.info(f"Support manager user updated by super admin {request.user.email}: {user.email}")
            return self.success_response(
                data=serializer.data,
                message='Support manager user updated successfully'
            )
            
        except Exception as exc:
            logger.error(f"Support manager user update error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while updating support manager user',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Delete support manager user (Super Admin only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_id'],
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID to delete'),
            }
        ),
        responses={
            200: openapi.Response('Support manager user deleted successfully'),
            400: 'Validation error',
            403: 'Access denied - only super admin can delete support manager users',
            404: 'User not found',
            500: 'Server error'
        },
        tags=['Support Manager'])
    def delete(self, request):
        """Delete support manager user"""
        try:
            if not request.user.is_super_admin():
                return self.error_response(
                    message='Access denied. Only super admin can delete support manager users.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            user_id = request.data.get('user_id')
            
            if not user_id:
                return self.error_response(
                    message='user_id is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(id=user_id, role='management')
            except User.DoesNotExist:
                return self.error_response(
                    message='Support manager user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            if user.id == request.user.id:
                return self.error_response(
                    message='Cannot delete your own account',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            user_email = user.email
            user.delete()
            
            logger.info(f"Support manager user deleted by super admin {request.user.email}: {user_email}")
            return self.success_response(
                message=f'Support manager user {user_email} deleted successfully'
            )
            
        except Exception as exc:
            logger.error(f"Support manager user deletion error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while deleting support manager user',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminPermissionGrantView(BaseAPIView):
    """Grant permissions to admin users - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="Grant permissions to admin users (Super Admin only)",
        request_body=AdminPermissionUpdateSerializer,
        responses={
            200: openapi.Response('Permissions granted successfully'),
            400: 'Validation error or invalid permission',
            403: 'Access denied - only super admin can grant permissions',
            404: 'Admin user not found',
            500: 'Server error'
        },
        tags=['Admin Permissions'])
    def post(self, request):
        """Grant permissions to admin user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                logger.warning(f"Permission grant attempt by non-super-admin: {request.user.email}")
                return self.error_response(
                    message='Access denied. Only super admin can grant permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            serializer = AdminPermissionUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return self.error_response(
                    message='Validation error',
                    data=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            admin_user_id = serializer.validated_data['admin_user_id']
            permissions = serializer.validated_data['permissions']
            
            # Get admin user
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    message='Admin user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Validate permissions
            valid_permissions = [choice[0] for choice in AdminPermission.PERMISSION_CHOICES]
            invalid_permissions = [p for p in permissions if p not in valid_permissions]
            if invalid_permissions:
                return self.error_response(
                    message=f'Invalid permissions: {", ".join(invalid_permissions)}',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Grant permissions
            with transaction.atomic():
                for permission in permissions:
                    AdminPermission.objects.get_or_create(
                        admin_user=admin_user,
                        permission=permission,
                        defaults={
                            'is_active': True,
                            'granted_by': request.user
                        }
                    )
            
            logger.info(f"Permissions granted to admin {admin_user.email} by super admin {request.user.email}")
            return self.success_response(
                data={'admin_user_id': admin_user_id, 'permissions': permissions},
                message=f'Permissions granted successfully to {admin_user.email}'
            )
            
        except Exception as exc:
            logger.error(f"Permission grant error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while granting permissions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminPermissionRevokeView(BaseAPIView):
    """Revoke permissions from admin users - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    @swagger_auto_schema(
        operation_description="Revoke permissions from admin users (Super Admin only)",
        request_body=AdminPermissionUpdateSerializer,
        responses={
            200: openapi.Response('Permissions revoked successfully'),
            400: 'Validation error or invalid permission',
            403: 'Access denied - only super admin can revoke permissions',
            404: 'Admin user not found',
            500: 'Server error'
        },
        tags=['Admin Permissions'])
    def post(self, request):
        """Revoke permissions from admin user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                logger.warning(f"Permission revoke attempt by non-super-admin: {request.user.email}")
                return self.error_response(
                    message='Access denied. Only super admin can revoke permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            serializer = AdminPermissionUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return self.error_response(
                    message='Validation error',
                    data=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            admin_user_id = serializer.validated_data['admin_user_id']
            permissions = serializer.validated_data['permissions']
            
            # Get admin user
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    message='Admin user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Validate permissions
            valid_permissions = [choice[0] for choice in AdminPermission.PERMISSION_CHOICES]
            invalid_permissions = [p for p in permissions if p not in valid_permissions]
            if invalid_permissions:
                return self.error_response(
                    message=f'Invalid permissions: {", ".join(invalid_permissions)}',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Revoke permissions
            with transaction.atomic():
                AdminPermission.objects.filter(
                    admin_user=admin_user,
                    permission__in=permissions
                ).update(is_active=False)
            
            logger.info(f"Permissions revoked from admin {admin_user.email} by super admin {request.user.email}")
            return self.success_response(
                data={'admin_user_id': admin_user_id, 'permissions': permissions},
                message=f'Permissions revoked successfully from {admin_user.email}'
            )
            
        except Exception as exc:
            logger.error(f"Permission revoke error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while revoking permissions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminPermissionListView(BaseAPIView):
    """List permissions for admin users - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

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
        tags=['Admin Permissions'])
    def get(self, request):
        """Get permissions for admin user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                logger.warning(f"Permission list attempt by non-super-admin: {request.user.email}")
                return self.error_response(
                    message='Access denied. Only super admin can view permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            admin_user_id = request.GET.get('admin_user_id')
            if not admin_user_id:
                return self.error_response(
                    message='admin_user_id is required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    message='Admin user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Get permissions
            permissions = AdminPermission.objects.filter(admin_user=admin_user, is_active=True)
            serializer = AdminPermissionSerializer(permissions, many=True)
            
            return self.success_response(
                data={
                    'admin_user': {
                        'id': admin_user.id,
                        'email': admin_user.email,
                        'first_name': admin_user.first_name,
                        'last_name': admin_user.last_name
                    },
                    'permissions': serializer.data
                },
                message=f'Permissions retrieved for {admin_user.email}'
            )
            
        except Exception as exc:
            logger.error(f"Permission list error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while retrieving permissions',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AdminPermissionDeleteView(BaseAPIView):
    """Delete specific permission for admin user - Super Admin only"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['delete']

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
        tags=['Admin Permissions'])
    def delete(self, request):
        """Delete specific permission for admin user"""
        try:
            # Check if user is super admin
            if not request.user.is_super_admin():
                logger.warning(f"Permission delete attempt by non-super-admin: {request.user.email}")
                return self.error_response(
                    message='Access denied. Only super admin can delete permissions.',
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            admin_user_id = request.data.get('admin_user_id')
            permission = request.data.get('permission')
            
            if not admin_user_id or not permission:
                return self.error_response(
                    message='admin_user_id and permission are required',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                admin_user = User.objects.get(id=admin_user_id, role='admin')
            except User.DoesNotExist:
                return self.error_response(
                    message='Admin user not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            # Delete permission
            deleted_count = AdminPermission.objects.filter(
                admin_user=admin_user,
                permission=permission
            ).delete()[0]
            
            if deleted_count == 0:
                return self.error_response(
                    message='Permission not found',
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            logger.info(f"Permission {permission} deleted for admin {admin_user.email} by super admin {request.user.email}")
            return self.success_response(
                message=f'Permission {permission} deleted successfully for {admin_user.email}'
            )
            
        except Exception as exc:
            logger.error(f"Permission delete error: {str(exc)}")
            return self.error_response(
                message='Server error occurred while deleting permission',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

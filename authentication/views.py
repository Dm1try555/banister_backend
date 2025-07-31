from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from .firebase_auth import verify_firebase_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, VerificationCode, Profile, EmailConfirmationCode, EmailConfirmationToken
from file_storage.models import ProfilePhoto, FileStorage  
import random
from rest_framework_simplejwt.tokens import RefreshToken
# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    UserNotFoundError, InvalidCredentialsError, EmailAlreadyExistsError,
    InvalidVerificationCodeError, ExpiredVerificationCodeError, BaseCustomException,
    InvalidEmailError, ValidationError, ServerError)
from error_handling.utils import ErrorResponseMixin, format_validation_errors
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
                                         'phone': openapi.Schema(type=openapi.TYPE_STRING, description='US phone number (optional) - Format: (XXX) XXX-XXXX'),
                     },
                     example={
                         'email': 'customer@example.com',
                         'password': 'password123',
                         'confirm_password': 'password123',
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
                'email': 'provider@example.com',
                'password': 'password123',
                'confirm_password': 'password123',
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
    """Manager registration"""
    permission_classes = [AllowAny]
    http_method_names = ['post']
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Manager registration (management)",
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
                'email': 'manager@example.com',
                'password': 'password123',
                'confirm_password': 'password123',
                'first_name': 'Admin',
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
    tags=['Authentication'])
class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh"""
    serializer_class = CustomTokenObtainPairSerializer

# --- Profile ---
class ProfileView(BaseAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'delete']

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
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        except Exception as e:
            return self.error_response(
                error_number='SERVER_ERROR',
                error_message=f'Failed to retrieve profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Update user profile (full update) - Role-specific fields",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING),
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
            400: 'Validation error or profile photo required for providers/managers',
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Profile'])
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        try:
            if request.user.role in ['provider', 'management'] and not request.user.has_required_profile_photo():
                return self.error_response(
                    error_number='PROFILE_PHOTO_REQUIRED',
                    error_message='Profile photo is required for providers and managers',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            return self.update(request, *args, **kwargs)
        except Exception as e:
            return self.error_response(
                error_number='SERVER_ERROR',
                error_message=f'Failed to update profile: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Update user profile (partial update) - Role-specific fields",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'role': openapi.Schema(type=openapi.TYPE_STRING),
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
            400: 'Validation error or profile photo required for providers/managers',
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Profile'])
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        try:
            if request.user.role in ['provider', 'management'] and not request.user.has_required_profile_photo():
                return self.error_response(
                    error_number='PROFILE_PHOTO_REQUIRED',
                    error_message='Profile photo is required for providers and managers',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            return self.partial_update(request, *args, **kwargs)
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

# --- Password ---
@swagger_auto_schema(
    operation_description="Request password reset by email",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email')
        },
        example={
            'email': 'user@example.com'
        }
    ),
    responses={
        200: openapi.Response('Reset link sent', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )),
        400: 'Email is required',
        404: 'User not found'
    },
    tags=['Password'])
class PasswordResetView(BaseAPIView):
    """Request password reset by email"""
    permission_classes = [AllowAny]
    http_method_names = ['post']
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return self.error_response(
                error_number='EMAIL_REQUIRED',
                error_message='Email is required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return self.error_response(
                error_number='USER_NOT_FOUND',
                error_message='User with this email not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Generate reset token
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(hours=1)
        
        # Delete old tokens for this user
        PasswordResetToken.objects.filter(email=email).delete()
        
        # Create new reset token
        PasswordResetToken.objects.create(
            email=email,
            token=token,
            expires_at=expires_at
        )
        
        # Send reset email
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = 'Password Reset Request'
        message = f'''
        Hello!
        
        You requested a password reset for your account.
        Click the link below to reset your password:
        
        {reset_url}
        
        This link is valid for 1 hour.
        
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
            return self.error_response(
                error_number='EMAIL_SEND_ERROR',
                error_message='Failed to send reset email',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return self.success_response(
            data={'email': email},
            message='Password reset link sent to your email'
        )


@swagger_auto_schema(
    operation_description="Reset password using token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token', 'new_password', 'confirm_password'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Reset token from email'),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Password confirmation')
        },
        example={
            'token': 'reset-token-here',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
    ),
    responses={
        200: openapi.Response('Password reset successful', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )),
        400: 'Invalid token, expired token, or passwords do not match',
        404: 'Token not found'
    },
    tags=['Password'])
class PasswordResetConfirmView(BaseAPIView):
    """Confirm password reset using token"""
    permission_classes = [AllowAny]
    http_method_names = ['post']
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([token, new_password, confirm_password]):
            return self.error_response(
                error_number='MISSING_FIELDS',
                error_message='Token, new_password, and confirm_password are required',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return self.error_response(
                error_number='PASSWORDS_DONT_MATCH',
                error_message='Passwords do not match',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password strength
        if len(new_password) < 8:
            return self.error_response(
                error_number='WEAK_PASSWORD',
                error_message='Password must be at least 8 characters long',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
        except PasswordResetToken.DoesNotExist:
            return self.error_response(
                error_number='INVALID_TOKEN',
                error_message='Invalid or used reset token',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        if reset_token.is_expired():
            return self.error_response(
                error_number='EXPIRED_TOKEN',
                error_message='Reset token has expired',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=reset_token.email)
        except User.DoesNotExist:
            return self.error_response(
                error_number='USER_NOT_FOUND',
                error_message='User not found',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.is_used = True
        reset_token.save()
        
        return self.success_response(
            data={'email': user.email},
            message='Password reset successful'
        )

@swagger_auto_schema(
    method='post',
    operation_description="User logout",
    responses={200: 'Logout successful'},
    tags=['Authentication'])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    return Response({'success': True, 'message': 'Logout successful'})

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
            'email': 'customer@example.com',
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
    tags=['Authentication'])
class CustomerLoginView(TokenObtainPairView):
    """Customer login"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        data['role'] = 'customer'
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            from error_handling.utils import create_error_response
            from error_handling.exceptions import AuthenticationError
            if isinstance(e, AuthenticationError):
                return create_error_response(
                    error_number='AUTHENTICATION_ERROR',
                    error_message=str(e),
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            else:
                return create_error_response(
                    error_number='AUTH_ERROR',
                    error_message=str(e),
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

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
            'email': 'provider@example.com',
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
    tags=['Authentication'])
class ProviderLoginView(TokenObtainPairView):
    """Provider login"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        data['role'] = 'provider'
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            from error_handling.utils import create_error_response
            from error_handling.exceptions import AuthenticationError
            if isinstance(e, AuthenticationError):
                return create_error_response(
                    error_number='AUTHENTICATION_ERROR',
                    error_message=str(e),
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            else:
                return create_error_response(
                    error_number='AUTH_ERROR',
                    error_message=str(e),
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

@swagger_auto_schema(
    operation_description="Manager authentication (management)",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'password'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        },
        example={
            'email': 'manager@example.com',
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
    tags=['Authentication'])
class ManagementLoginView(TokenObtainPairView):
    """Manager login"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        data['role'] = 'management'
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            from error_handling.utils import create_error_response
            from error_handling.exceptions import AuthenticationError
            if isinstance(e, AuthenticationError):
                return create_error_response(
                    error_number='AUTHENTICATION_ERROR',
                    error_message=str(e),
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            else:
                return create_error_response(
                    error_number='AUTH_ERROR',
                    error_message=str(e),
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Email for confirmation')
        }
    ),
    responses={
        200: openapi.Response('Link sent', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
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

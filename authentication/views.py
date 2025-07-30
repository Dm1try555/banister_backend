from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from .firebase_auth import verify_firebase_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, VerificationCode, Profile, EmailConfirmationCode, EmailConfirmationToken
import random
from rest_framework_simplejwt.tokens import RefreshToken

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    UserNotFoundError, InvalidCredentialsError, EmailAlreadyExistsError,
    InvalidVerificationCodeError, ExpiredVerificationCodeError, BaseCustomException,
    InvalidEmailError, ValidationError
)
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


def handle_registration_errors(exc):
    """Handle registration errors"""
    from rest_framework.exceptions import ValidationError as DRFValidationError
    
    if isinstance(exc, DRFValidationError) or hasattr(exc, 'detail'):
        errors = exc.detail if hasattr(exc, 'detail') else exc.args[0]
        if isinstance(errors, dict) and 'email' in errors:
            email_errors = errors['email']
            if isinstance(email_errors, list):
                email_errors = email_errors
            else:
                email_errors = [email_errors]
            
            for error in email_errors:
                error_str = str(error).lower()
                if 'valid email address' in error_str or 'invalid email' in error_str:
                    raise InvalidEmailError('Invalid email')
                if 'already exists' in error_str:
                    raise EmailAlreadyExistsError('User with this email already exists')
        
        raise ValidationError('Data validation error')
    raise exc


# --- Registration ---
@swagger_auto_schema(
    method='post',
    operation_description="Customer registration (customer)",
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response('Successful registration', UserSerializer),
        400: 'Validation error or user already exists'
    },
    tags=['Registration']
)
@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def register_customer(request):
    serializer = RegisterSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save(role='customer')
        return Response(serializer.data, status=201)
    except Exception as exc:
        handle_registration_errors(exc)

@swagger_auto_schema(
    method='post',
    operation_description="Provider registration (provider)",
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response('Successful registration', UserSerializer),
        400: 'Validation error or user already exists'
    },
    tags=['Registration']
)
@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def register_provider(request):
    serializer = RegisterSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save(role='provider')
        return Response(serializer.data, status=201)
    except Exception as exc:
        handle_registration_errors(exc)

@swagger_auto_schema(
    method='post',
    operation_description="Manager registration (management)",
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response('Successful registration', UserSerializer),
        400: 'Validation error or user already exists'
    },
    tags=['Registration']
)
@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def register_management(request):
    serializer = RegisterSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save(role='management')
        return Response(serializer.data, status=201)
    except Exception as exc:
        handle_registration_errors(exc)

class FirebaseAuthView(BaseAPIView):
    """Firebase authentication"""
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def post(self, request, provider):
        id_token = request.data.get('id_token')
        role = request.data.get('role', 'customer')
        
        if not id_token:
            from error_handling.exceptions import ValidationError
            raise ValidationError('Token not provided')
        
        decoded_token = verify_firebase_token(id_token)
        
        email = decoded_token.get('email')
        uid = decoded_token.get('uid')
        
        if not email:
            from error_handling.exceptions import ValidationError
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

# --- Profile ---
@swagger_auto_schema(
    operation_description="Get and update user profile",
    tags=['Profile']
)
class ProfileView(BaseAPIView,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):
    """User profile management"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# --- Password ---
@swagger_auto_schema(
    operation_description="Reset user password by email",
    tags=['Password']
)
class PasswordResetView(BaseAPIView):
    """User password reset"""
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        return self.error_response(
            error_number='NOT_IMPLEMENTED',
            error_message='Password reset not implemented',
            status_code=501
        )

@swagger_auto_schema(
    method='post',
    operation_description="User logout",
    responses={200: 'Logout successful'},
    tags=['Authentication']
)
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
        # Here should be email/SMS sending
        return code

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            
            if self.user_check_required:
                if not User.objects.filter(email=email) and not User.objects.filter(phone=phone):
                    raise UserNotFoundError('User not found')
            
            code = self.send_code(email, phone)
            
            return self.success_response(
                data={'code': code},  # In production, remove the code
                message='Confirmation code sent'
            )
            
        except BaseCustomException:
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
            
            # Check for code expiration (e.g., 10 minutes)
            from django.utils import timezone
            from datetime import timedelta
            
            if vcode.created_at < timezone.now() - timedelta(minutes=10):
                raise ExpiredVerificationCodeError('Confirmation code expired')
            
            vcode.is_used = True
            vcode.save()
            
            return vcode
            
        except VerificationCode.DoesNotExist:
            raise InvalidVerificationCodeError('Invalid confirmation code')

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
                try:
                    user = User.objects.get(email=email) if email else User.objects.get(phone=phone)
                except User.DoesNotExist:
                    raise UserNotFoundError('User not found')
            
            token = CustomTokenObtainPairSerializer.get_token(user)
            
            return self.success_response(
                data={
                    'access': str(token.access_token),
                    'refresh': str(token),
                    'role': user.role
                },
                message='Successful verification'
            )
            
        except BaseCustomException:
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

    @swagger_auto_schema(
        operation_description="Customer authentication (customer)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'role': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        data['role'] = 'customer'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class ProviderLoginView(TokenObtainPairView):
    """Provider login"""
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Provider authentication (provider)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'role': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        data['role'] = 'provider'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class ManagementLoginView(TokenObtainPairView):
    """Manager login"""
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Manager authentication (management)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'role': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        data['role'] = 'management'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

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
    tags=['Email confirmation']
)
@api_view(['POST'])
@permission_classes([AllowAny])
def email_confirm_request(request):
    """Send email confirmation link"""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=400)
    
    # Create a token with expiration of 24 hours
    token = str(uuid.uuid4())
    expires_at = timezone.now() + timedelta(hours=24)
    
    # Delete old tokens for this email
    EmailConfirmationToken.objects.filter(email=email).delete()
    
    # Create a new token
    EmailConfirmationToken.objects.create(
        email=email,
        token=token,
        expires_at=expires_at
    )
    
    # Form the confirmation link
    confirmation_url = f"{settings.FRONTEND_URL}/confirm-email?token={token}"
    
    # Send email with plain text
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
    
    return Response({
        'success': True, 
        'message': 'Email confirmation link sent'
    }, status=200)

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
    tags=['Email confirmation']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def email_confirm_verify(request):
    """Verify email by token from link"""
    token = request.GET.get('token')
    
    if not token:
        return Response({'error': 'Token is required'}, status=400)
    
    try:
        confirmation = EmailConfirmationToken.objects.get(
            token=token, 
            is_used=False
        )
    except EmailConfirmationToken.DoesNotExist:
        return Response({'error': 'Invalid or used token'}, status=400)
    
    # Check expiration
    if confirmation.is_expired():
        return Response({'error': 'Token expired'}, status=400)
    
    # Mark token as used
    confirmation.is_used = True
    confirmation.save()
    
    # Mark email as confirmed in user profile
    try:
        user = User.objects.get(email=confirmation.email)
        profile = Profile.objects.get(user=user)
        profile.is_email_confirmed = True
        profile.save()
    except (User.DoesNotExist, Profile.DoesNotExist):
        pass  # If user or profile does not exist, just skip
    
    return Response({
        'success': True, 
        'message': 'Email confirmed successfully'
    }, status=200)
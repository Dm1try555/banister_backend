from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction
import logging

from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode
from core.error_handling.utils import create_success_response
from .models import User, PasswordResetCode, EmailConfirmationToken
from core.authentication.tasks import send_password_reset_email

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

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
    """Request password reset code"""
    from core.error_handling.enums import ErrorCode
    from core.error_handling.utils import create_error_response, create_success_response
    
    email_address = request.data.get('email')
    
    if not email_address:
        return create_error_response(ErrorCode.EMAIL_ALREADY_EXISTS, 'Email is required')
    
    try:
        user = User.objects.get(email=email_address)
    except User.DoesNotExist:
        return create_error_response(ErrorCode.USER_DELETED, 'User not found')
    
    # Generate 6-digit code
    import random
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Save reset code
    PasswordResetCode.objects.create(
        email=email_address,
        code=code
    )
    
    # Send email using inherited MailMixin method
    try:
        send_password_reset_email.delay(email_address, code)
        logger.info(f"Password reset code sent to: {email_address}")
    except Exception as e:
        logger.error(f"Failed to send password reset email to {email_address}: {str(e)}")
        return create_error_response(ErrorCode.EMAIL_SERVICE_SMTP_ERROR, 'Failed to send password reset email')
    
    return create_success_response({'email': email_address}, 'Password reset code sent to your email')

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
    from core.error_handling.enums import ErrorCode
    from core.error_handling.utils import create_error_response, create_success_response
    
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    
    if not all([email, code, new_password]):
        return create_error_response(ErrorCode.EMAIL_ALREADY_EXISTS, 'Email, code, and new password are required')
    
    # Validate password strength
    if len(new_password) < 8:
        return create_error_response(ErrorCode.PASSWORD_TOO_WEAK, 'Password must be at least 8 characters long')
    
    try:
        reset_code = PasswordResetCode.objects.get(email=email, code=code, is_used=False)
    except PasswordResetCode.DoesNotExist:
        return create_error_response(ErrorCode.INVALID_VERIFICATION_CODE, 'Invalid reset code')
    
    if reset_code.is_expired():
        return create_error_response(ErrorCode.EXPIRED_VERIFICATION_CODE, 'Reset code has expired')
    
    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        
        # Mark code as used
        reset_code.is_used = True
        reset_code.save()
        
        logger.info(f"Password reset successful for user: {email}")
        
        return create_success_response({'email': email}, 'Password reset successful')
    except User.DoesNotExist:
        return create_error_response(ErrorCode.USER_DELETED, 'User not found')
    except Exception as e:
        logger.error(f"Error resetting password for {email}: {str(e)}")
        return create_error_response(ErrorCode.USER_DELETED, f'Error resetting password: {str(e)}')

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
    """User logout"""
    from core.error_handling.utils import create_success_response
    
    logger.info(f"User logged out: {request.user.email}")
    
    return create_success_response(None, 'Logout successful')

@swagger_auto_schema(
    method='post',
    operation_description="Send email confirmation link",
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
        200: openapi.Response('Email confirmation sent'),
        400: 'Email is required',
        404: 'User not found'
    },
    tags=['Email Confirmation'])
@api_view(['POST'])
@permission_classes([AllowAny])
def email_confirm_request(request):
    """Send email confirmation link"""
    from core.error_handling.enums import ErrorCode
    from core.error_handling.utils import create_error_response, create_success_response
    
    email = request.data.get('email')
    if not email:
        return create_error_response(ErrorCode.EMAIL_ALREADY_EXISTS, 'Email is required')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return create_error_response(ErrorCode.USER_DELETED, 'User not found')
    
    # Generate confirmation token
    import uuid
    token = str(uuid.uuid4())
    
    # Save token
    EmailConfirmationToken.objects.create(
        email=email,
        token=token
    )
    
    # Send confirmation email
    try:
        # TODO: Implement email sending
        logger.info(f"Email confirmation token generated for: {email}")
    except Exception as e:
        logger.error(f"Failed to send email confirmation to {email}: {str(e)}")
        return create_error_response(ErrorCode.EMAIL_SERVICE_SMTP_ERROR, 'Failed to send confirmation email')
    
    return create_success_response(None, 'Email confirmation sent')

@swagger_auto_schema(
    method='get',
    operation_description="Verify email by token from link",
    manual_parameters=[
        openapi.Parameter(
            'token',
            openapi.IN_QUERY,
            description='Email confirmation token',
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Email confirmed successfully'),
        400: 'Invalid or expired token',
        404: 'Token not found'
    },
    tags=['Email Confirmation'])
@api_view(['GET'])
@permission_classes([AllowAny])
def email_confirm_verify(request):
    """Verify email by token from link"""
    from core.error_handling.enums import ErrorCode
    from core.error_handling.utils import create_error_response, create_success_response
    
    token = request.GET.get('token')
    if not token:
        return create_error_response(ErrorCode.INVALID_VERIFICATION_CODE, 'Token is required')

    try:
        confirmation = EmailConfirmationToken.objects.get(token=token, is_used=False)
    except EmailConfirmationToken.DoesNotExist:
        return create_error_response(ErrorCode.INVALID_VERIFICATION_CODE, 'Invalid or used token')

    if confirmation.is_expired():
        return create_error_response(ErrorCode.EXPIRED_VERIFICATION_CODE, 'Token expired')
    
    try:
        user = User.objects.get(email=confirmation.email)
        user.is_email_verified = True
        user.save()
        
        # Mark token as used
        confirmation.is_used = True
        confirmation.save()
        
        logger.info(f"Email confirmed for user: {confirmation.email}")
        
        return create_success_response(None, 'Email confirmed successfully')
    except User.DoesNotExist:
        return create_error_response(ErrorCode.USER_DELETED, 'User not found')
    except Exception as e:
        logger.error(f"Error confirming email for {confirmation.email}: {str(e)}")
        return create_error_response(ErrorCode.USER_DELETED, f'Error confirming email: {str(e)}') 
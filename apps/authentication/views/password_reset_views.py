from core.base.common_imports import *
from ..models import User, VerificationCode
from ..serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Request password reset",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate and save reset code
            reset_code = VerificationCode.create_code(
                user=user,
                code_type='password_reset',
                expiry_minutes=10
            )
            
            # Send password reset email
            html_message = render_to_string('emails/password_reset_email.html', {
                'username': user.username,
                'reset_code': reset_code.code,
                'reset_url': f"{settings.FRONTEND_URL}/reset-password" if hasattr(settings, 'FRONTEND_URL') else '/reset-password',
                'support_url': f"{settings.FRONTEND_URL}/support" if hasattr(settings, 'FRONTEND_URL') else '/support'
            })
            
            send_mail(
                subject='Reset Your Password - Banister',
                message=f'Your password reset code is: {reset_code.code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({
                'message': 'Password reset email sent successfully. Code expires in 10 minutes.'
            })
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            ErrorCode.EMAIL_SEND_FAILED.raise_error()


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Confirm password reset with code",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']
        new_password_confirm = serializer.validated_data['new_password_confirm']
        
        try:
            user = User.objects.get(email=email)
            
            # Find and validate reset code
            try:
                reset_code = VerificationCode.objects.get(
                    user=user,
                    code=code,
                    code_type='password_reset',
                    is_used=False
                )
            except VerificationCode.DoesNotExist:
                raise CustomValidationError(ErrorCode.INVALID_VERIFICATION_CODE)
            
            if not reset_code.is_valid():
                raise CustomValidationError(ErrorCode.VERIFICATION_CODE_EXPIRED)
            
            # Set new password and mark code as used
            user.set_password(new_password)
            user.save()
            reset_code.mark_as_used()
            
            return Response({
                'message': 'Password reset successfully.'
            })
            
        except User.DoesNotExist:
            raise CustomValidationError(ErrorCode.EMAIL_NOT_FOUND)
        except CustomValidationError:
            raise
        except Exception as e:
            logger.error(f"Failed to reset password: {e}")
            raise CustomValidationError(ErrorCode.PASSWORD_RESET_FAILED)


password_reset_request = PasswordResetRequestView.as_view()
password_reset_confirm = PasswordResetConfirmView.as_view() 
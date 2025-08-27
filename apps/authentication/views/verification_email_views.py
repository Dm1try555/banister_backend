from core.base.common_imports import *
from ..models import User, VerificationCode
from ..serializers import SendVerificationEmailSerializer, VerifyEmailSerializer
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SendVerificationEmailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Send verification email to user",
        request_body=SendVerificationEmailSerializer,
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
        serializer = SendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate and save verification code
            verification_code = VerificationCode.create_code(
                user=user,
                code_type='email_verification',
                expiry_minutes=10
            )
            
            # Send verification email
            html_message = render_to_string('emails/verification_email.html', {
                'username': user.username,
                'verification_code': verification_code.code,
                'verification_url': f"{settings.FRONTEND_URL}/verify-email" if hasattr(settings, 'FRONTEND_URL') else '/verify-email',
                'support_url': f"{settings.FRONTEND_URL}/support" if hasattr(settings, 'FRONTEND_URL') else '/support'
            })
            
            send_mail(
                subject='Verify Your Email - Banister',
                message=f'Your verification code is: {verification_code.code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({
                'message': 'Verification email sent successfully. Code expires in 10 minutes.'
            })
            
        except User.DoesNotExist:
            ErrorCode.USER_NOT_FOUND.raise_error()
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {e}")
            ErrorCode.EMAIL_SEND_FAILED.raise_error()


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verify user email with code",
        request_body=VerifyEmailSerializer,
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
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        try:
            user = User.objects.get(email=email)
            
            # Find and validate verification code
            try:
                verification_code = VerificationCode.objects.get(
                    user=user,
                    code=code,
                    code_type='email_verification',
                    is_used=False
                )
            except VerificationCode.DoesNotExist:
                ErrorCode.INVALID_VERIFICATION_CODE.raise_error()
            
            if not verification_code.is_valid():
                ErrorCode.VERIFICATION_CODE_EXPIRED.raise_error()
            
            # Mark email as verified and code as used
            user.email_verified = True
            user.save()
            verification_code.mark_as_used()
            
            return Response({
                'message': 'Email verified successfully.'
            })
            
        except User.DoesNotExist:
            ErrorCode.USER_NOT_FOUND.raise_error()
        except Exception as e:
            logger.error(f"Failed to verify email for {email}: {e}")
            ErrorCode.EMAIL_VERIFICATION_FAILED.raise_error()


send_verification_email = SendVerificationEmailView.as_view()
verify_email = VerifyEmailView.as_view() 
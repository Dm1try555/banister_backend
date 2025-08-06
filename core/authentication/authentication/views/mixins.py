from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random
import logging

from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode
from .models import VerificationCode, User
from core.authentication.tasks import send_verification_code_email

logger = logging.getLogger(__name__)

class VerificationCodeSenderMixin:
    """Mixin for sending confirmation code by email or phone"""
    serializer_class = None
    user_check_required = False
    
    def send_code(self, email, phone):
        """Send verification code"""
        try:
            # Generate 6-digit code
            code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            # Save code to database
            VerificationCode.objects.create(
                email=email,
                phone=phone,
                code=code,
                expires_at=timezone.now() + timedelta(minutes=10)
            )
            
            # Send email
            if email:
                send_verification_code_email.delay(email, code)
                logger.info(f"Verification code sent to email: {email}")
            
            return True
        except Exception as e:
            logger.error(f"Error sending verification code: {str(e)}")
            return False
    
    @transaction.atomic
    def post(self, request):
        """Send verification code"""
        try:
            email = request.data.get('email')
            phone = request.data.get('phone')
            
            if not email and not phone:
                return self.error_response(
                    ErrorCode.EMAIL_ALREADY_EXISTS,
                    'Email or phone is required'
                )
            
            # Check if user exists (if required)
            if self.user_check_required:
                try:
                    user = User.objects.get(email=email) if email else User.objects.get(phone=phone)
                    if user.is_active:
                        return self.error_response(
                            ErrorCode.EMAIL_ALREADY_EXISTS,
                            'User already exists'
                        )
                except User.DoesNotExist:
                    pass
            
            # Send code
            if self.send_code(email, phone):
                return self.success_response(
                    data={'email': email, 'phone': phone},
                    message='Verification code sent successfully'
                )
            else:
                return self.error_response(
                    ErrorCode.EMAIL_SERVICE_SMTP_ERROR,
                    'Failed to send verification code'
                )
                
        except Exception as e:
            logger.error(f"Error in verification code sender: {str(e)}")
            return self.error_response(
                ErrorCode.EMAIL_SERVICE_SMTP_ERROR,
                f'Error sending verification code: {str(e)}'
            )


class VerificationCodeVerifyMixin:
    """Mixin for verifying confirmation code and issuing token"""
    serializer_class = None
    create_user_if_not_exists = False
    
    def verify_code(self, email, phone, code):
        """Verify code and return user"""
        try:
            # Find verification code
            verification_code = VerificationCode.objects.get(
                email=email,
                phone=phone,
                code=code,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            
            # Mark as used
            verification_code.is_used = True
            verification_code.save()
            
            # Get or create user
            if self.create_user_if_not_exists:
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'phone': phone,
                        'is_active': True
                    }
                )
                if created:
                    logger.info(f"New user created via verification: {email}")
            else:
                user = User.objects.get(email=email) if email else User.objects.get(phone=phone)
            
            return user
        except VerificationCode.DoesNotExist:
            return None
        except User.DoesNotExist:
            return None
    
    @transaction.atomic
    def post(self, request):
        """Verify code and issue token"""
        try:
            email = request.data.get('email')
            phone = request.data.get('phone')
            code = request.data.get('code')
            
            if not code:
                return self.error_response(
                    ErrorCode.INVALID_VERIFICATION_CODE,
                    'Verification code is required'
                )
            
            # Verify code
            user = self.verify_code(email, phone, code)
            if not user:
                return self.error_response(
                    ErrorCode.INVALID_VERIFICATION_CODE,
                    'Invalid or expired verification code'
                )
            
            # Generate tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"User verified successfully: {user.email}")
            
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
                message='Verification successful'
            )
                
        except Exception as e:
            logger.error(f"Error in verification code verify: {str(e)}")
            return self.error_response(
                ErrorCode.INVALID_VERIFICATION_CODE,
                f'Error verifying code: {str(e)}'
            ) 
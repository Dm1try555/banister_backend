from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from core.error_handling.enums import ErrorCode
from core.error_handling.exceptions import CustomValidationError
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Centralized email service for all email operations"""
    
    @staticmethod
    def send_email(subject, recipient_email, template_name, context=None, plain_message=None, async_send=True):
        """
        Send email with HTML template
        
        Args:
            subject: Email subject
            recipient_email: Recipient email address
            template_name: Template name (e.g., 'emails/verification_email.html')
            context: Template context variables
            plain_message: Plain text fallback message
            async_send: Whether to send email asynchronously via Celery
        """
        try:
            if async_send:
                # Send email asynchronously via Celery
                from .tasks import send_email_task
                return send_email_task.delay(
                    subject=subject,
                    recipient_email=recipient_email,
                    template_name=template_name,
                    context=context,
                    plain_message=plain_message
                )
            else:
                # Send email synchronously using the same logic as Celery task
                from .tasks import _send_email_sync
                return _send_email_sync(
                    subject=subject,
                    recipient_email=recipient_email,
                    template_name=template_name,
                    context=context,
                    plain_message=plain_message
                )
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")
            raise CustomValidationError(ErrorCode.EMAIL_SEND_FAILED)
    
    @staticmethod
    def send_verification_email(user, verification_code, async_send=True):
        """Send email verification email"""
        context = {
            'username': user.username,
            'verification_code': verification_code.code,
            'verification_url': f"{getattr(settings, 'FRONTEND_URL', '')}/verify-email"
        }
        
        return EmailService.send_email(
            subject='Verify Your Email - Banister',
            recipient_email=user.email,
            template_name='emails/verification_email.html',
            context=context,
            plain_message=f'Your verification code is: {verification_code.code}',
            async_send=async_send
        )
    
    @staticmethod
    def send_password_reset_email(user, reset_code, async_send=True):
        """Send password reset email"""
        context = {
            'username': user.username,
            'reset_code': reset_code.code,
            'reset_url': f"{getattr(settings, 'FRONTEND_URL', '')}/reset-password"
        }
        
        return EmailService.send_email(
            subject='Reset Your Password - Banister',
            recipient_email=user.email,
            template_name='emails/password_reset_email.html',
            context=context,
            plain_message=f'Your password reset code is: {reset_code.code}',
            async_send=async_send
        )
    
    @staticmethod
    def send_welcome_email(user, async_send=True):
        """Send welcome email to new user"""
        context = {
            'username': user.username,
            'login_url': f"{getattr(settings, 'FRONTEND_URL', '')}/login"
        }
        
        return EmailService.send_email(
            subject='Welcome to Banister! 🎉',
            recipient_email=user.email,
            template_name='emails/welcome_email.html',
            context=context,
            plain_message=f'Welcome {user.username}! Thank you for joining Banister.',
            async_send=async_send
        )


# Create singleton instance
email_service = EmailService()
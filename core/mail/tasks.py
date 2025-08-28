from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from core.error_handling.enums import ErrorCode
from core.error_handling.exceptions import CustomValidationError
import logging

logger = logging.getLogger(__name__)


def _send_email_sync(subject, recipient_email, template_name, context=None, plain_message=None):
    """
    Synchronous email sending function (shared between service and tasks)
    
    Args:
        subject: Email subject
        recipient_email: Recipient email address
        template_name: Template name (e.g., 'emails/verification_email.html')
        context: Template context variables
        plain_message: Plain text fallback message
    """
    context = context or {}
    
    # Add common context variables
    context.update({
        'frontend_url': getattr(settings, 'FRONTEND_URL', ''),
        'support_url': f"{getattr(settings, 'FRONTEND_URL', '')}/support"
    })
    
    # Render HTML template
    html_message = render_to_string(template_name, context)
    
    # Use plain message if provided, otherwise extract from HTML
    if not plain_message:
        plain_message = f"Please check the HTML version of this email."
    
    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        html_message=html_message,
        fail_silently=False,
    )
    
    logger.info(f"Email sent successfully to {recipient_email}")
    return True


@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, recipient_email, template_name, context=None, plain_message=None):
    """
    Celery task for sending emails asynchronously
    
    Args:
        subject: Email subject
        recipient_email: Recipient email address
        template_name: Template name (e.g., 'emails/verification_email.html')
        context: Template context variables
        plain_message: Plain text fallback message
    """
    try:
        _send_email_sync(subject, recipient_email, template_name, context, plain_message)
        return f"Email sent to {recipient_email}"
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        raise CustomValidationError(ErrorCode.EMAIL_SEND_FAILED)


@shared_task(bind=True, max_retries=3)
def send_verification_email_task(self, user_id, verification_code):
    """Celery task for sending verification email"""
    try:
        from apps.authentication.models import User
        
        user = User.objects.get(id=user_id)
        context = {
            'username': user.username,
            'verification_code': verification_code,
            'verification_url': f"{getattr(settings, 'FRONTEND_URL', '')}/verify-email"
        }
        
        return send_email_task.delay(
            subject='Verify Your Email - Banister',
            recipient_email=user.email,
            template_name='emails/verification_email.html',
            context=context,
            plain_message=f'Your verification code is: {verification_code}'
        )
        
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        raise CustomValidationError(ErrorCode.EMAIL_SEND_FAILED)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email_task(self, user_id, reset_code):
    """Celery task for sending password reset email"""
    try:
        from apps.authentication.models import User
        
        user = User.objects.get(id=user_id)
        context = {
            'username': user.username,
            'reset_code': reset_code,
            'reset_url': f"{getattr(settings, 'FRONTEND_URL', '')}/reset-password"
        }
        
        return send_email_task.delay(
            subject='Reset Your Password - Banister',
            recipient_email=user.email,
            template_name='emails/password_reset_email.html',
            context=context,
            plain_message=f'Your password reset code is: {reset_code}'
        )
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        raise CustomValidationError(ErrorCode.EMAIL_SEND_FAILED)


@shared_task(bind=True, max_retries=3)
def send_welcome_email_task(self, user_id):
    """Celery task for sending welcome email"""
    try:
        from apps.authentication.models import User
        
        user = User.objects.get(id=user_id)
        context = {
            'username': user.username,
            'login_url': f"{getattr(settings, 'FRONTEND_URL', '')}/login"
        }
        
        return send_email_task.delay(
            subject='Welcome to Banister! 🎉',
            recipient_email=user.email,
            template_name='emails/welcome_email.html',
            context=context,
            plain_message=f'Welcome {user.username}! Thank you for joining Banister.'
        )
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        raise CustomValidationError(ErrorCode.EMAIL_SEND_FAILED)


@shared_task(bind=True, max_retries=3)
def send_bulk_email_task(self, email_list, subject, template_name, context=None):
    """
    Celery task for sending bulk emails
    
    Args:
        email_list: List of email addresses
        subject: Email subject
        template_name: Template name
        context: Template context variables
    """
    try:
        context = context or {}
        results = []
        
        for email in email_list:
            try:
                result = send_email_task.delay(
                    subject=subject,
                    recipient_email=email,
                    template_name=template_name,
                    context=context
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to queue email for {email}: {e}")
                results.append(None)
        
        return f"Queued {len(results)} emails"
        
    except Exception as e:
        logger.error(f"Failed to send bulk emails: {e}")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        raise CustomValidationError(ErrorCode.EMAIL_SEND_FAILED)
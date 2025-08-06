import logging
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from .models import VerificationCode
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(
    name='authentication.tasks.cleanup_expired_verification_codes',
    queue='email'
)
def cleanup_expired_verification_codes():
    """
    Периодическая задача для очистки устаревших кодов подтверждения
    """
    try:
        # Удаляем коды, которые старше 24 часов
        cutoff_time = timezone.now() - timedelta(hours=24)
        deleted_count = VerificationCode.objects.filter(
            created_at__lt=cutoff_time
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} expired verification codes")
        return {
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Cleaned up {deleted_count} expired verification codes'
        }
        
    except Exception as exc:
        logger.error(f"Error cleaning up expired verification codes: {str(exc)}", exc_info=True)
        return {
            'success': False,
            'message': f'Error: {str(exc)}'
        }


@shared_task(
    name='authentication.tasks.send_verification_code_email',
    queue='email',
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def send_verification_code_email(
    email: str,
    code: str,
    subject: str = "Код подтверждения",
    template_name: str = "authentication/verification_code_email.html"
):
    """
    Асинхронная отправка email с кодом подтверждения
    
    Args:
        email: Email получателя
        code: Код подтверждения
        subject: Тема письма
        template_name: Имя шаблона
    """
    try:
        from core.mail.async_service import async_mail_service
        
        context = {
            'code': code,
            'expires_in': '10 минут'
        }
        
        task_result = async_mail_service.send_template_email_async(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[email]
        )
        
        logger.info(f"Verification code email queued for {email}")
        return {
            'success': True,
            'email': email,
            'task_id': task_result.id,
            'message': 'Verification code email queued successfully'
        }
        
    except Exception as exc:
        logger.error(f"Error sending verification code email to {email}: {str(exc)}", exc_info=True)
        return {
            'success': False,
            'email': email,
            'message': f'Error: {str(exc)}'
        }


@shared_task(
    name='authentication.tasks.send_welcome_email',
    queue='email',
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def send_welcome_email(
    email: str,
    username: str,
    subject: str = "Добро пожаловать в Banister!",
    template_name: str = "authentication/welcome_email.html"
):
    """
    Асинхронная отправка приветственного email
    
    Args:
        email: Email получателя
        username: Имя пользователя
        subject: Тема письма
        template_name: Имя шаблона
    """
    try:
        from core.mail.async_service import async_mail_service
        
        context = {
            'username': username,
            'login_url': f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/login"
        }
        
        task_result = async_mail_service.send_template_email_async(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[email]
        )
        
        logger.info(f"Welcome email queued for {email}")
        return {
            'success': True,
            'email': email,
            'task_id': task_result.id,
            'message': 'Welcome email queued successfully'
        }
        
    except Exception as exc:
        logger.error(f"Error sending welcome email to {email}: {str(exc)}", exc_info=True)
        return {
            'success': False,
            'email': email,
            'message': f'Error: {str(exc)}'
        }


@shared_task(
    name='authentication.tasks.send_password_reset_email',
    queue='email',
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def send_password_reset_email(
    email: str,
    reset_token: str,
    subject: str = "Сброс пароля",
    template_name: str = "authentication/password_reset_email.html"
):
    """
    Асинхронная отправка email для сброса пароля
    
    Args:
        email: Email получателя
        reset_token: Токен для сброса пароля
        subject: Тема письма
        template_name: Имя шаблона
    """
    try:
        from core.mail.async_service import async_mail_service
        
        reset_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        context = {
            'reset_url': reset_url,
            'expires_in': '1 час'
        }
        
        task_result = async_mail_service.send_template_email_async(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=[email]
        )
        
        logger.info(f"Password reset email queued for {email}")
        return {
            'success': True,
            'email': email,
            'task_id': task_result.id,
            'message': 'Password reset email queued successfully'
        }
        
    except Exception as exc:
        logger.error(f"Error sending password reset email to {email}: {str(exc)}", exc_info=True)
        return {
            'success': False,
            'email': email,
            'message': f'Error: {str(exc)}'
        } 
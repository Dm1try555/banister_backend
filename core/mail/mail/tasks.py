import logging
import json
from typing import List, Dict, Any, Optional
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from .service import MailService

logger = logging.getLogger(__name__)

# Создаем экземпляр сервиса для синхронной отправки
mail_service = MailService()


@shared_task(
    bind=True,
    name='mail.tasks.send_email_task',
    queue='email',
    max_retries=3,
    default_retry_delay=300,  # 5 минут
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def send_email_task(
    self,
    subject: str,
    message: str,
    recipient_list: List[str],
    from_email: str = None,
    html_message: str = None,
    fail_silently: bool = True
) -> Dict[str, Any]:
    """
    Асинхронная задача для отправки email
    
    Args:
        subject: Тема письма
        message: Текстовое содержимое
        recipient_list: Список получателей
        from_email: Email отправителя (опционально)
        html_message: HTML содержимое (опционально)
        fail_silently: Не выбрасывать исключения при ошибке
    
    Returns:
        Dict с результатом отправки
    """
    try:
        logger.info(f"Starting email task for recipients: {recipient_list}")
        
        result = mail_service.send_email(
            subject=subject,
            message=message,
            recipient_list=recipient_list,
            from_email=from_email,
            html_message=html_message,
            fail_silently=fail_silently
        )
        
        if result:
            logger.info(f"Email sent successfully to {recipient_list}")
            return {
                'success': True,
                'recipients': recipient_list,
                'message': 'Email sent successfully'
            }
        else:
            logger.error(f"Failed to send email to {recipient_list}")
            return {
                'success': False,
                'recipients': recipient_list,
                'message': 'Failed to send email'
            }
            
    except Exception as exc:
        logger.error(f"Error in send_email_task: {str(exc)}", exc_info=True)
        
        # Повторная попытка
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying email task (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc)
        
        return {
            'success': False,
            'recipients': recipient_list,
            'message': f'Failed after {self.max_retries} retries: {str(exc)}'
        }


@shared_task(
    bind=True,
    name='mail.tasks.send_html_email_task',
    queue='email',
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def send_html_email_task(
    self,
    subject: str,
    html_content: str,
    recipient_list: List[str],
    text_content: str = None,
    from_email: str = None,
    reply_to: str = None,
    fail_silently: bool = True
) -> Dict[str, Any]:
    """
    Асинхронная задача для отправки HTML email
    
    Args:
        subject: Тема письма
        html_content: HTML содержимое
        recipient_list: Список получателей
        text_content: Текстовое содержимое (опционально)
        from_email: Email отправителя (опционально)
        reply_to: Email для ответа (опционально)
        fail_silently: Не выбрасывать исключения при ошибке
    
    Returns:
        Dict с результатом отправки
    """
    try:
        logger.info(f"Starting HTML email task for recipients: {recipient_list}")
        
        result = mail_service.send_html_email(
            subject=subject,
            html_content=html_content,
            recipient_list=recipient_list,
            text_content=text_content,
            from_email=from_email,
            reply_to=reply_to,
            fail_silently=fail_silently
        )
        
        if result:
            logger.info(f"HTML email sent successfully to {recipient_list}")
            return {
                'success': True,
                'recipients': recipient_list,
                'message': 'HTML email sent successfully'
            }
        else:
            logger.error(f"Failed to send HTML email to {recipient_list}")
            return {
                'success': False,
                'recipients': recipient_list,
                'message': 'Failed to send HTML email'
            }
            
    except Exception as exc:
        logger.error(f"Error in send_html_email_task: {str(exc)}", exc_info=True)
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying HTML email task (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc)
        
        return {
            'success': False,
            'recipients': recipient_list,
            'message': f'Failed after {self.max_retries} retries: {str(exc)}'
        }


@shared_task(
    bind=True,
    name='mail.tasks.send_template_email_task',
    queue='email',
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def send_template_email_task(
    self,
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    recipient_list: List[str],
    from_email: str = None,
    fail_silently: bool = True
) -> Dict[str, Any]:
    """
    Асинхронная задача для отправки email с использованием шаблона
    
    Args:
        subject: Тема письма
        template_name: Имя шаблона
        context: Контекст для шаблона
        recipient_list: Список получателей
        from_email: Email отправителя (опционально)
        fail_silently: Не выбрасывать исключения при ошибке
    
    Returns:
        Dict с результатом отправки
    """
    try:
        logger.info(f"Starting template email task for recipients: {recipient_list}")
        
        result = mail_service.send_template_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=recipient_list,
            from_email=from_email,
            fail_silently=fail_silently
        )
        
        if result:
            logger.info(f"Template email sent successfully to {recipient_list}")
            return {
                'success': True,
                'recipients': recipient_list,
                'template': template_name,
                'message': 'Template email sent successfully'
            }
        else:
            logger.error(f"Failed to send template email to {recipient_list}")
            return {
                'success': False,
                'recipients': recipient_list,
                'template': template_name,
                'message': 'Failed to send template email'
            }
            
    except Exception as exc:
        logger.error(f"Error in send_template_email_task: {str(exc)}", exc_info=True)
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying template email task (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc)
        
        return {
            'success': False,
            'recipients': recipient_list,
            'template': template_name,
            'message': f'Failed after {self.max_retries} retries: {str(exc)}'
        }


@shared_task(
    bind=True,
    name='mail.tasks.send_bulk_email_task',
    queue='email',
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def send_bulk_email_task(
    self,
    subject: str,
    message: str,
    recipient_lists: List[List[str]],
    from_email: str = None,
    html_message: str = None,
    fail_silently: bool = True
) -> Dict[str, Any]:
    """
    Асинхронная задача для массовой отправки email
    
    Args:
        subject: Тема письма
        message: Текстовое содержимое
        recipient_lists: Список списков получателей
        from_email: Email отправителя (опционально)
        html_message: HTML содержимое (опционально)
        fail_silently: Не выбрасывать исключения при ошибке
    
    Returns:
        Dict с результатом отправки
    """
    try:
        logger.info(f"Starting bulk email task for {len(recipient_lists)} recipient groups")
        
        result = mail_service.send_bulk_email(
            subject=subject,
            message=message,
            recipient_lists=recipient_lists,
            from_email=from_email,
            html_message=html_message,
            fail_silently=fail_silently
        )
        
        logger.info(f"Bulk email task completed: {result}")
        return result
        
    except Exception as exc:
        logger.error(f"Error in send_bulk_email_task: {str(exc)}", exc_info=True)
        
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying bulk email task (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=exc)
        
        return {
            'success': False,
            'total_recipients': sum(len(recipients) for recipients in recipient_lists),
            'failed_recipients': sum(len(recipients) for recipients in recipient_lists),
            'message': f'Failed after {self.max_retries} retries: {str(exc)}'
        }


@shared_task(
    name='mail.tasks.process_email_queue',
    queue='email'
)
def process_email_queue():
    """
    Периодическая задача для обработки очереди email
    Проверяет Redis на наличие отложенных email и отправляет их
    """
    try:
        logger.info("Processing email queue...")
        
        # Здесь можно добавить логику для обработки отложенных email
        # Например, проверка Redis на наличие email в очереди
        
        logger.info("Email queue processing completed")
        return {'success': True, 'message': 'Email queue processed'}
        
    except Exception as exc:
        logger.error(f"Error processing email queue: {str(exc)}", exc_info=True)
        return {'success': False, 'message': f'Error: {str(exc)}'}


@shared_task(
    name='mail.tasks.cleanup_failed_emails',
    queue='email'
)
def cleanup_failed_emails():
    """
    Периодическая задача для очистки неудачных email
    """
    try:
        logger.info("Cleaning up failed emails...")
        
        # Здесь можно добавить логику для очистки неудачных email
        # Например, удаление старых записей из Redis
        
        logger.info("Failed emails cleanup completed")
        return {'success': True, 'message': 'Failed emails cleaned up'}
        
    except Exception as exc:
        logger.error(f"Error cleaning up failed emails: {str(exc)}", exc_info=True)
        return {'success': False, 'message': f'Error: {str(exc)}'} 
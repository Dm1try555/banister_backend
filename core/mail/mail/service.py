import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from typing import List, Dict, Any, Optional, Tuple, Union
from celery.result import AsyncResult

logger = logging.getLogger(__name__)


class MailService:
    """Централизованный сервис для отправки email"""
    
    def __init__(self):
        self.default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@banister.com')
        self.default_reply_to = getattr(settings, 'DEFAULT_REPLY_TO', 'support@banister.com')
    
    def send_email(
        self,
        subject: str,
        message: str,
        recipient_list: List[str],
        from_email: str = None,
        html_message: str = None,
        fail_silently: bool = False
    ) -> bool:
        """
        Отправить простое email сообщение
        
        Args:
            subject: Тема письма
            message: Текстовое содержимое
            recipient_list: Список получателей
            from_email: Email отправителя (опционально)
            html_message: HTML содержимое (опционально)
            fail_silently: Не выбрасывать исключения при ошибке
        
        Returns:
            bool: Успех отправки
        """
        try:
            from_email = from_email or self.default_from_email
            
            result = send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=fail_silently
            )
            
            if result:
                logger.info(f"Email sent successfully to {recipient_list}")
            else:
                logger.error(f"Failed to send email to {recipient_list}")
            
            return bool(result)
            
        except Exception as e:
            error_msg = f"Error sending email: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if not fail_silently:
                raise
            
            return False
    
    def send_html_email(
        self,
        subject: str,
        html_content: str,
        recipient_list: List[str],
        text_content: str = None,
        from_email: str = None,
        reply_to: str = None,
        fail_silently: bool = False
    ) -> bool:
        """
        Отправить HTML email сообщение
        
        Args:
            subject: Тема письма
            html_content: HTML содержимое
            recipient_list: Список получателей
            text_content: Текстовое содержимое (опционально)
            from_email: Email отправителя (опционально)
            reply_to: Email для ответа (опционально)
            fail_silently: Не выбрасывать исключения при ошибке
        
        Returns:
            bool: Успех отправки
        """
        try:
            from_email = from_email or self.default_from_email
            reply_to = reply_to or self.default_reply_to
            
            if text_content:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email,
                    to=recipient_list,
                    reply_to=[reply_to]
                )
                email.attach_alternative(html_content, "text/html")
            else:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=html_content,
                    from_email=from_email,
                    to=recipient_list,
                    reply_to=[reply_to]
                )
                email.content_subtype = "html"
            
            result = email.send()
            
            if result:
                logger.info(f"HTML email sent successfully to {recipient_list}")
            else:
                logger.error(f"Failed to send HTML email to {recipient_list}")
            
            return bool(result)
            
        except Exception as e:
            error_msg = f"Error sending HTML email: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if not fail_silently:
                raise
            
            return False
    
    def send_template_email(
        self,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        recipient_list: List[str],
        from_email: str = None,
        fail_silently: bool = False
    ) -> bool:
        """
        Отправить email используя шаблон
        
        Args:
            subject: Тема письма
            template_name: Название шаблона
            context: Контекст для шаблона
            recipient_list: Список получателей
            from_email: Email отправителя (опционально)
            fail_silently: Не выбрасывать исключения при ошибке
        
        Returns:
            bool: Успех отправки
        """
        try:
            # Рендерим шаблон
            html_content = render_to_string(template_name, context)
            
            return self.send_html_email(
                subject=subject,
                html_content=html_content,
                recipient_list=recipient_list,
                from_email=from_email,
                fail_silently=fail_silently
            )
            
        except Exception as e:
            error_msg = f"Error sending template email: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            if not fail_silently:
                raise
            
            return False
    
    def send_bulk_email(
        self,
        subject: str,
        message: str,
        recipient_lists: List[List[str]],
        from_email: str = None,
        html_message: str = None,
        fail_silently: bool = False
    ) -> Dict[str, Any]:
        """
        Отправить массовые email сообщения
        
        Args:
            subject: Тема письма
            message: Текстовое содержимое
            recipient_lists: Список списков получателей
            from_email: Email отправителя (опционально)
            html_message: HTML содержимое (опционально)
            fail_silently: Не выбрасывать исключения при ошибке
        
        Returns:
            Dict[str, Any]: Результаты отправки
        """
        results = {
            'total': len(recipient_lists),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for recipient_list in recipient_lists:
            try:
                success = self.send_email(
                    subject=subject,
                    message=message,
                    recipient_list=recipient_list,
                    from_email=from_email,
                    html_message=html_message,
                    fail_silently=fail_silently
                )
                
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'recipients': recipient_list,
                        'error': 'Failed to send email'
                    })
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'recipients': recipient_list,
                    'error': str(e)
                })
        
        logger.info(f"Bulk email completed: {results['sent']} sent, {results['failed']} failed")
        return results


# Создаем глобальный экземпляр сервиса
mail_service = MailService()

# Импортируем асинхронный сервис
from .async_service import async_mail_service 
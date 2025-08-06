import logging
from typing import List, Dict, Any, Optional, Union
from celery.result import AsyncResult
from django.conf import settings
from .tasks import (
    send_email_task,
    send_html_email_task,
    send_template_email_task,
    send_bulk_email_task
)

logger = logging.getLogger(__name__)


class AsyncMailService:
    """
    Асинхронный сервис для отправки email через Redis очереди
    """
    
    def __init__(self):
        self.default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@banister.com')
        self.default_reply_to = getattr(settings, 'DEFAULT_REPLY_TO', 'support@banister.com')
    
    def send_email_async(
        self,
        subject: str,
        message: str,
        recipient_list: List[str],
        from_email: str = None,
        html_message: str = None,
        fail_silently: bool = True,
        countdown: int = 0,
        eta: Optional[str] = None
    ) -> AsyncResult:
        """
        Асинхронная отправка простого email сообщения
        
        Args:
            subject: Тема письма
            message: Текстовое содержимое
            recipient_list: Список получателей
            from_email: Email отправителя (опционально)
            html_message: HTML содержимое (опционально)
            fail_silently: Не выбрасывать исключения при ошибке
            countdown: Задержка в секундах перед отправкой
            eta: Точное время отправки (ISO формат)
        
        Returns:
            AsyncResult: Результат асинхронной задачи
        """
        try:
            from_email = from_email or self.default_from_email
            
            logger.info(f"Queueing email task for recipients: {recipient_list}")
            
            task_result = send_email_task.apply_async(
                kwargs={
                    'subject': subject,
                    'message': message,
                    'recipient_list': recipient_list,
                    'from_email': from_email,
                    'html_message': html_message,
                    'fail_silently': fail_silently
                },
                countdown=countdown,
                eta=eta
            )
            
            logger.info(f"Email task queued with ID: {task_result.id}")
            return task_result
            
        except Exception as e:
            error_msg = f"Error queueing email task: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
    
    def send_html_email_async(
        self,
        subject: str,
        html_content: str,
        recipient_list: List[str],
        text_content: str = None,
        from_email: str = None,
        reply_to: str = None,
        fail_silently: bool = True,
        countdown: int = 0,
        eta: Optional[str] = None
    ) -> AsyncResult:
        """
        Асинхронная отправка HTML email сообщения
        
        Args:
            subject: Тема письма
            html_content: HTML содержимое
            recipient_list: Список получателей
            text_content: Текстовое содержимое (опционально)
            from_email: Email отправителя (опционально)
            reply_to: Email для ответа (опционально)
            fail_silently: Не выбрасывать исключения при ошибке
            countdown: Задержка в секундах перед отправкой
            eta: Точное время отправки (ISO формат)
        
        Returns:
            AsyncResult: Результат асинхронной задачи
        """
        try:
            from_email = from_email or self.default_from_email
            reply_to = reply_to or self.default_reply_to
            
            logger.info(f"Queueing HTML email task for recipients: {recipient_list}")
            
            task_result = send_html_email_task.apply_async(
                kwargs={
                    'subject': subject,
                    'html_content': html_content,
                    'recipient_list': recipient_list,
                    'text_content': text_content,
                    'from_email': from_email,
                    'reply_to': reply_to,
                    'fail_silently': fail_silently
                },
                countdown=countdown,
                eta=eta
            )
            
            logger.info(f"HTML email task queued with ID: {task_result.id}")
            return task_result
            
        except Exception as e:
            error_msg = f"Error queueing HTML email task: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
    
    def send_template_email_async(
        self,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        recipient_list: List[str],
        from_email: str = None,
        fail_silently: bool = True,
        countdown: int = 0,
        eta: Optional[str] = None
    ) -> AsyncResult:
        """
        Асинхронная отправка email с использованием шаблона
        
        Args:
            subject: Тема письма
            template_name: Имя шаблона
            context: Контекст для шаблона
            recipient_list: Список получателей
            from_email: Email отправителя (опционально)
            fail_silently: Не выбрасывать исключения при ошибке
            countdown: Задержка в секундах перед отправкой
            eta: Точное время отправки (ISO формат)
        
        Returns:
            AsyncResult: Результат асинхронной задачи
        """
        try:
            from_email = from_email or self.default_from_email
            
            logger.info(f"Queueing template email task for recipients: {recipient_list}")
            
            task_result = send_template_email_task.apply_async(
                kwargs={
                    'subject': subject,
                    'template_name': template_name,
                    'context': context,
                    'recipient_list': recipient_list,
                    'from_email': from_email,
                    'fail_silently': fail_silently
                },
                countdown=countdown,
                eta=eta
            )
            
            logger.info(f"Template email task queued with ID: {task_result.id}")
            return task_result
            
        except Exception as e:
            error_msg = f"Error queueing template email task: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
    
    def send_bulk_email_async(
        self,
        subject: str,
        message: str,
        recipient_lists: List[List[str]],
        from_email: str = None,
        html_message: str = None,
        fail_silently: bool = True,
        countdown: int = 0,
        eta: Optional[str] = None
    ) -> AsyncResult:
        """
        Асинхронная массовая отправка email
        
        Args:
            subject: Тема письма
            message: Текстовое содержимое
            recipient_lists: Список списков получателей
            from_email: Email отправителя (опционально)
            html_message: HTML содержимое (опционально)
            fail_silently: Не выбрасывать исключения при ошибке
            countdown: Задержка в секундах перед отправкой
            eta: Точное время отправки (ISO формат)
        
        Returns:
            AsyncResult: Результат асинхронной задачи
        """
        try:
            from_email = from_email or self.default_from_email
            
            total_recipients = sum(len(recipients) for recipients in recipient_lists)
            logger.info(f"Queueing bulk email task for {len(recipient_lists)} groups, {total_recipients} total recipients")
            
            task_result = send_bulk_email_task.apply_async(
                kwargs={
                    'subject': subject,
                    'message': message,
                    'recipient_lists': recipient_lists,
                    'from_email': from_email,
                    'html_message': html_message,
                    'fail_silently': fail_silently
                },
                countdown=countdown,
                eta=eta
            )
            
            logger.info(f"Bulk email task queued with ID: {task_result.id}")
            return task_result
            
        except Exception as e:
            error_msg = f"Error queueing bulk email task: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Получить статус задачи по ID
        
        Args:
            task_id: ID задачи Celery
        
        Returns:
            Dict с информацией о статусе задачи
        """
        try:
            result = AsyncResult(task_id)
            
            status_info = {
                'task_id': task_id,
                'status': result.status,
                'ready': result.ready(),
                'successful': result.successful(),
                'failed': result.failed(),
            }
            
            if result.ready():
                if result.successful():
                    status_info['result'] = result.result
                else:
                    status_info['error'] = str(result.info)
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting task status for {task_id}: {str(e)}")
            return {
                'task_id': task_id,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Отменить задачу по ID
        
        Args:
            task_id: ID задачи Celery
        
        Returns:
            bool: Успех отмены
        """
        try:
            result = AsyncResult(task_id)
            result.revoke(terminate=True)
            logger.info(f"Task {task_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {str(e)}")
            return False
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Получить статистику очередей
        
        Returns:
            Dict с информацией о очередях
        """
        try:
            # Здесь можно добавить логику для получения статистики из Redis
            # Например, количество задач в очереди, активные воркеры и т.д.
            
            return {
                'email_queue': {
                    'active_tasks': 0,  # Заглушка
                    'pending_tasks': 0,  # Заглушка
                    'completed_tasks': 0,  # Заглушка
                    'failed_tasks': 0,  # Заглушка
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting queue stats: {str(e)}")
            return {'error': str(e)}


# Создаем глобальный экземпляр асинхронного сервиса
async_mail_service = AsyncMailService() 
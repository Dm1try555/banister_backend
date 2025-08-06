from typing import Dict, Any
from .service import core.mail_service
from .utils import core.mail_utils


class MailMixin:
    """Миксин для добавления email функциональности к моделям"""
    
    def send_welcome_email(self) -> bool:
        """Отправить приветственное письмо"""
        return mail_utils.send_welcome_email(self.email, getattr(self, 'first_name', None))
    
    def send_password_reset_email(self, reset_url: str) -> bool:
        """Отправить письмо для сброса пароля"""
        return mail_utils.send_password_reset_email(self.email, reset_url)
    
    def send_password_reset_code_email(self, reset_code: str) -> bool:
        """Отправить письмо с кодом для сброса пароля"""
        subject = 'Password Reset Code - Banister'
        message = f'''
        Hello,
        
        You requested a password reset for your Banister account.
        
        Your reset code is: {reset_code}
        
        This code is valid for 10 minutes.
        
        If you did not request this reset, please ignore this email.
        '''
        
        return mail_utils.send_custom_email(self.email, subject, message)
    
    def send_email_confirmation_email(self, confirmation_url: str) -> bool:
        """Отправить письмо для подтверждения email"""
        return mail_utils.send_email_confirmation_email(self.email, confirmation_url)
    
    def send_custom_email(self, subject: str, message: str) -> bool:
        """Отправить кастомное email сообщение"""
        return mail_utils.send_custom_email(self.email, subject, message)


class BookingMailMixin:
    """Миксин для email функциональности бронирований"""
    
    def send_booking_confirmation_email(self, user_email: str) -> bool:
        """Отправить письмо подтверждения бронирования"""
        booking_details = {
            'service_name': getattr(self.service, 'title', 'N/A') if hasattr(self, 'service') else 'N/A',
            'date': getattr(self, 'scheduled_datetime', 'N/A'),
            'time': getattr(self, 'scheduled_datetime', 'N/A'),
            'provider_name': getattr(self.provider, 'email', 'N/A') if hasattr(self, 'provider') else 'N/A'
        }
        return mail_utils.send_booking_confirmation_email(user_email, booking_details)


class PaymentMailMixin:
    """Миксин для email функциональности платежей"""
    
    def send_payment_confirmation_email(self, user_email: str) -> bool:
        """Отправить письмо подтверждения платежа"""
        payment_details = {
            'amount': getattr(self, 'amount', 'N/A'),
            'date': getattr(self, 'created_at', 'N/A'),
            'transaction_id': getattr(self, 'transaction_id', 'N/A')
        }
        return mail_utils.send_payment_confirmation_email(user_email, payment_details)


class NotificationMailMixin:
    """Миксин для email функциональности уведомлений"""
    
    def send_notification_email(self, user_email: str) -> bool:
        """Отправить уведомление по email"""
        notification_title = getattr(self, 'title', 'Notification')
        notification_message = getattr(self, 'message', 'You have a new notification.')
        return mail_utils.send_notification_email(user_email, notification_title, notification_message)


class MailServiceMixin:
    """Миксин для прямого доступа к mail сервису"""
    
    def send_email(
        self,
        subject: str,
        message: str,
        recipient_list: list,
        from_email: str = None,
        html_message: str = None,
        fail_silently: bool = False
    ) -> bool:
        """Отправить простое email сообщение"""
        return mail_service.send_email(
            subject=subject,
            message=message,
            recipient_list=recipient_list,
            from_email=from_email,
            html_message=html_message,
            fail_silently=fail_silently
        )
    
    def send_html_email(
        self,
        subject: str,
        html_content: str,
        recipient_list: list,
        text_content: str = None,
        from_email: str = None,
        reply_to: str = None,
        fail_silently: bool = False
    ) -> bool:
        """Отправить HTML email сообщение"""
        return mail_service.send_html_email(
            subject=subject,
            html_content=html_content,
            recipient_list=recipient_list,
            text_content=text_content,
            from_email=from_email,
            reply_to=reply_to,
            fail_silently=fail_silently
        )
    
    def send_template_email(
        self,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        recipient_list: list,
        from_email: str = None,
        fail_silently: bool = False
    ) -> bool:
        """Отправить email используя шаблон"""
        return mail_service.send_template_email(
            subject=subject,
            template_name=template_name,
            context=context,
            recipient_list=recipient_list,
            from_email=from_email,
            fail_silently=fail_silently
        )
    
    def send_bulk_email(
        self,
        subject: str,
        message: str,
        recipient_lists: list,
        from_email: str = None,
        html_message: str = None,
        fail_silently: bool = False
    ) -> Dict[str, Any]:
        """Отправить массовые email сообщения"""
        return mail_service.send_bulk_email(
            subject=subject,
            message=message,
            recipient_lists=recipient_lists,
            from_email=from_email,
            html_message=html_message,
            fail_silently=fail_silently
        ) 
from typing import List, Dict, Any
from .service import core.mail_service


class MailUtils:
    """Утилиты для работы с email"""
    
    @staticmethod
    def send_welcome_email(user_email: str, user_name: str = None) -> bool:
        """Отправить приветственное письмо"""
        subject = "Welcome to Banister!"
        message = f"""
        Hello {user_name or user_email},
        
        Welcome to Banister! We're excited to have you on board.
        
        Your account has been successfully created. You can now:
        - Browse available services
        - Book appointments with providers
        - Manage your profile and preferences
        - Track your bookings and payments
        
        If you have any questions, please contact our support team.
        
        Best regards,
        The Banister Team
        """
        
        return mail_service.send_email(
            subject=subject,
            message=message,
            recipient_list=[user_email]
        )
    
    @staticmethod
    def send_password_reset_email(user_email: str, reset_url: str) -> bool:
        """Отправить письмо для сброса пароля"""
        subject = "Password Reset Request - Banister"
        message = f"""
        Hello,
        
        We received a request to reset your password for your Banister account.
        
        If you made this request, please click the link below to reset your password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        The Banister Team
        """
        
        return mail_service.send_email(
            subject=subject,
            message=message,
            recipient_list=[user_email]
        )
    
    @staticmethod
    def send_email_confirmation_email(user_email: str, confirmation_url: str) -> bool:
        """Отправить письмо для подтверждения email"""
        subject = "Confirm Your Email - Banister"
        message = f"""
        Hello,
        
        Please confirm your email address by clicking the link below:
        {confirmation_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account with Banister, please ignore this email.
        
        Best regards,
        The Banister Team
        """
        
        return mail_service.send_email(
            subject=subject,
            message=message,
            recipient_list=[user_email]
        )
    
    @staticmethod
    def send_booking_confirmation_email(user_email: str, booking_details: Dict[str, Any]) -> bool:
        """Отправить письмо подтверждения бронирования"""
        subject = "Booking Confirmation - Banister"
        message = f"""
        Hello,
        
        Your booking has been confirmed!
        
        Booking Details:
        - Service: {booking_details.get('service_name', 'N/A')}
        - Date: {booking_details.get('date', 'N/A')}
        - Time: {booking_details.get('time', 'N/A')}
        - Provider: {booking_details.get('provider_name', 'N/A')}
        
        Thank you for choosing Banister!
        
        Best regards,
        The Banister Team
        """
        
        return mail_service.send_email(
            subject=subject,
            message=message,
            recipient_list=[user_email]
        )
    
    @staticmethod
    def send_payment_confirmation_email(user_email: str, payment_details: Dict[str, Any]) -> bool:
        """Отправить письмо подтверждения платежа"""
        subject = "Payment Confirmation - Banister"
        message = f"""
        Hello,
        
        Your payment has been successfully processed!
        
        Payment Details:
        - Amount: ${payment_details.get('amount', 'N/A')}
        - Date: {payment_details.get('date', 'N/A')}
        - Transaction ID: {payment_details.get('transaction_id', 'N/A')}
        
        Thank you for your payment!
        
        Best regards,
        The Banister Team
        """
        
        return mail_service.send_email(
            subject=subject,
            message=message,
            recipient_list=[user_email]
        )
    
    @staticmethod
    def send_notification_email(user_email: str, notification_title: str, notification_message: str) -> bool:
        """Отправить уведомление по email"""
        subject = f"Notification: {notification_title} - Banister"
        message = f"""
        Hello,
        
        {notification_message}
        
        Best regards,
        The Banister Team
        """
        
        return mail_service.send_email(
            subject=subject,
            message=message,
            recipient_list=[user_email]
        )
    
    @staticmethod
    def send_custom_email(user_email: str, subject: str, message: str) -> bool:
        """Отправить кастомное email сообщение"""
        return mail_service.send_email(
            subject=subject,
            message=message,
            recipient_list=[user_email]
        )


# Создаем глобальный экземпляр утилит
mail_utils = MailUtils() 
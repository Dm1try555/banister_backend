from .models import Notification
from .firebase_service import firebase_service
from core.authentication.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def send_notification(user_id, notification_type, data=None, fcm_token=None):
    """
    Отправить уведомление пользователю
    
    Args:
        user_id (int): ID пользователя
        notification_type (str): Тип уведомления
        data (dict): Дополнительные данные
        fcm_token (str): FCM токен устройства (опционально)
    
    Returns:
        Notification: Созданное уведомление или None при ошибке
    """
    try:
        # Получаем пользователя
        user = User.objects.get(id=user_id)
        
        # Создаем уведомление в базе данных
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            data=data or {},
            fcm_token=fcm_token
        )
        
        # Отправляем push-уведомление через Firebase
        if fcm_token:
            title = _get_notification_title(notification_type)
            body = _get_notification_body(notification_type, data)
            
            firebase_service.send_notification(
                fcm_token=fcm_token,
                title=title,
                body=body,
                data=data or {}
            )
        
        logger.info(f"Уведомление отправлено пользователю {user.email}: {notification_type}")
        return notification
        
    except User.DoesNotExist:
        logger.error(f"Пользователь с ID {user_id} не найден")
        return None
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {str(e)}")
        return None


def send_notification_to_admin(notification_type, data=None, fcm_token=None):
    """
    Отправить уведомление администратору
    
    Args:
        notification_type (str): Тип уведомления
        data (dict): Дополнительные данные
        fcm_token (str): FCM токен устройства (опционально)
    
    Returns:
        list: Список созданных уведомлений
    """
    try:
        # Получаем всех администраторов
        admins = User.objects.filter(is_staff=True, is_active=True)
        
        notifications = []
        for admin in admins:
            notification = send_notification(
                user_id=admin.id,
                notification_type=notification_type,
                data=data,
                fcm_token=fcm_token
            )
            if notification:
                notifications.append(notification)
        
        logger.info(f"Уведомления отправлены {len(notifications)} администраторам: {notification_type}")
        return notifications
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомлений администраторам: {str(e)}")
        return []


def send_booking_notification_to_admin(booking_data):
    """
    Отправить уведомление о новом бронировании администратору
    
    Args:
        booking_data (dict): Данные бронирования
    
    Returns:
        list: Список созданных уведомлений
    """
    return send_notification_to_admin(
        notification_type='ClientSendBookingNotigicationToAdmin',
        data=booking_data
    )


def send_payment_notification(user_id, payment_data, fcm_token=None):
    """
    Отправить уведомление о платеже
    
    Args:
        user_id (int): ID пользователя
        payment_data (dict): Данные платежа
        fcm_token (str): FCM токен устройства (опционально)
    
    Returns:
        Notification: Созданное уведомление или None при ошибке
    """
    notification_type = 'PaymentReceived' if payment_data.get('status') == 'success' else 'PaymentFailed'
    
    return send_notification(
        user_id=user_id,
        notification_type=notification_type,
        data=payment_data,
        fcm_token=fcm_token
    )


def send_booking_status_notification(user_id, booking_data, status, fcm_token=None):
    """
    Отправить уведомление об изменении статуса бронирования
    
    Args:
        user_id (int): ID пользователя
        booking_data (dict): Данные бронирования
        status (str): Новый статус бронирования
        fcm_token (str): FCM токен устройства (опционально)
    
    Returns:
        Notification: Созданное уведомление или None при ошибке
    """
    notification_type = 'BookingConfirmed' if status == 'confirmed' else 'BookingCancelled'
    
    return send_notification(
        user_id=user_id,
        notification_type=notification_type,
        data=booking_data,
        fcm_token=fcm_token
    )


def _get_notification_title(notification_type):
    """Получить заголовок уведомления по типу"""
    titles = {
        'ClientSendBookingNotigicationToAdmin': 'Новое бронирование',
        'BookingConfirmed': 'Бронирование подтверждено',
        'BookingCancelled': 'Бронирование отменено',
        'PaymentReceived': 'Платеж получен',
        'PaymentFailed': 'Ошибка платежа',
        'ServiceUpdated': 'Услуга обновлена',
        'NewMessage': 'Новое сообщение',
        'SystemAlert': 'Системное уведомление',
    }
    return titles.get(notification_type, 'Новое уведомление')


def _get_notification_body(notification_type, data):
    """Получить текст уведомления по типу и данным"""
    if notification_type == 'ClientSendBookingNotigicationToAdmin':
        client_name = data.get('client_name', 'Клиент')
        service_name = data.get('service_name', 'услуга')
        return f"Новое бронирование от {client_name} для {service_name}"
    elif notification_type == 'BookingConfirmed':
        return f"Ваше бронирование подтверждено"
    elif notification_type == 'BookingCancelled':
        return f"Бронирование отменено"
    elif notification_type == 'PaymentReceived':
        amount = data.get('amount', '')
        return f"Платеж на сумму {amount} успешно получен"
    elif notification_type == 'PaymentFailed':
        return f"Ошибка при обработке платежа"
    elif notification_type == 'ServiceUpdated':
        service_name = data.get('service_name', 'услуга')
        return f"Информация об услуге '{service_name}' обновлена"
    elif notification_type == 'NewMessage':
        sender_name = data.get('sender_name', 'пользователь')
        return f"Новое сообщение от {sender_name}"
    elif notification_type == 'SystemAlert':
        return f"Системное уведомление"
    else:
        return "У вас новое уведомление"


def get_user_notifications_count(user_id, status='unread'):
    """
    Получить количество уведомлений пользователя
    
    Args:
        user_id (int): ID пользователя
        status (str): Статус уведомлений для подсчета
    
    Returns:
        int: Количество уведомлений
    """
    try:
        return Notification.objects.filter(user_id=user_id, status=status).count()
    except Exception as e:
        logger.error(f"Ошибка подсчета уведомлений: {str(e)}")
        return 0


def mark_user_notifications_as_read(user_id, notification_ids=None):
    """
    Отметить уведомления пользователя как прочитанные
    
    Args:
        user_id (int): ID пользователя
        notification_ids (list): Список ID уведомлений (если None - все уведомления)
    
    Returns:
        int: Количество обновленных уведомлений
    """
    try:
        queryset = Notification.objects.filter(user_id=user_id, status='unread')
        
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        updated_count = queryset.update(
            status='read',
            read_at=timezone.now()
        )
        
        logger.info(f"Отмечено как прочитанные {updated_count} уведомлений пользователя {user_id}")
        return updated_count
        
    except Exception as e:
        logger.error(f"Ошибка отметки уведомлений как прочитанных: {str(e)}")
        return 0 
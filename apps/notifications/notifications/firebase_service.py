import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)


class FirebaseService:
    """Сервис для работы с Firebase Cloud Messaging"""
    
    def __init__(self):
        self.app = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Инициализация Firebase"""
        try:
            # Проверяем, инициализировано ли уже Firebase
            if not firebase_admin._apps:
                # Путь к файлу сервисного аккаунта Firebase
                service_account_path = os.path.join(settings.BASE_DIR, 'firebase-service-account.json')
                
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    self.app = firebase_admin.initialize_app(cred)
                    logger.info("Firebase инициализирован успешно")
                else:
                    logger.warning(f"Файл сервисного аккаунта Firebase не найден: {service_account_path}")
                    self.app = None
            else:
                self.app = firebase_admin.get_app()
                logger.info("Firebase уже инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Firebase: {str(e)}")
            self.app = None
    
    def send_notification(self, fcm_token, title, body, data=None):
        """
        Отправить push-уведомление через Firebase
        
        Args:
            fcm_token (str): FCM токен устройства
            title (str): Заголовок уведомления
            body (str): Текст уведомления
            data (dict): Дополнительные данные
        """
        if not self.app or not fcm_token:
            logger.warning("Firebase не инициализирован или FCM токен отсутствует")
            return False
        
        try:
            # Создаем сообщение
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=fcm_token,
            )
            
            # Отправляем сообщение
            response = messaging.send(message)
            logger.info(f"Уведомление отправлено успешно: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {str(e)}")
            return False
    
    def send_multicast_notification(self, fcm_tokens, title, body, data=None):
        """
        Отправить push-уведомление нескольким устройствам
        
        Args:
            fcm_tokens (list): Список FCM токенов устройств
            title (str): Заголовок уведомления
            body (str): Текст уведомления
            data (dict): Дополнительные данные
        """
        if not self.app or not fcm_tokens:
            logger.warning("Firebase не инициализирован или FCM токены отсутствуют")
            return False
        
        try:
            # Создаем сообщение для множественной отправки
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=fcm_tokens,
            )
            
            # Отправляем сообщение
            response = messaging.send_multicast(message)
            logger.info(f"Множественные уведомления отправлены: {response.success_count}/{len(fcm_tokens)}")
            return response.success_count > 0
            
        except Exception as e:
            logger.error(f"Ошибка отправки множественных уведомлений: {str(e)}")
            return False
    
    def send_topic_notification(self, topic, title, body, data=None):
        """
        Отправить push-уведомление по теме
        
        Args:
            topic (str): Тема уведомления
            title (str): Заголовок уведомления
            body (str): Текст уведомления
            data (dict): Дополнительные данные
        """
        if not self.app:
            logger.warning("Firebase не инициализирован")
            return False
        
        try:
            # Создаем сообщение для темы
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic,
            )
            
            # Отправляем сообщение
            response = messaging.send(message)
            logger.info(f"Уведомление по теме '{topic}' отправлено: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления по теме: {str(e)}")
            return False


# Создаем глобальный экземпляр сервиса
firebase_service = FirebaseService() 
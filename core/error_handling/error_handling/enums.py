from enum import Enum
from rest_framework import status


class ErrorCode(Enum):
    
    # Кастомные ошибки аутентификации (1000-1999)
    USER_DELETED = (1000, "Аккаунт пользователя удален", status.HTTP_401_UNAUTHORIZED)
    INVALID_VERIFICATION_CODE = (1001, "Неверный код подтверждения", status.HTTP_400_BAD_REQUEST)
    EXPIRED_VERIFICATION_CODE = (1002, "Код подтверждения истек", status.HTTP_400_BAD_REQUEST)
    EMAIL_ALREADY_EXISTS = (1003, "Email уже существует", status.HTTP_400_BAD_REQUEST)
    PHONE_ALREADY_EXISTS = (1004, "Телефон уже существует", status.HTTP_400_BAD_REQUEST)
    PASSWORD_TOO_WEAK = (1005, "Пароль слишком слабый", status.HTTP_400_BAD_REQUEST)
    
    # Кастомные ошибки бизнес-логики (2000-2999)
    BOOKING_NOT_FOUND = (2000, "Бронирование не найдено", status.HTTP_404_NOT_FOUND)
    SERVICE_NOT_FOUND = (2001, "Услуга не найдена", status.HTTP_404_NOT_FOUND)
    PROVIDER_NOT_FOUND = (2002, "Поставщик не найден", status.HTTP_404_NOT_FOUND)
    BOOKING_CONFLICT = (2003, "Конфликт бронирования", status.HTTP_409_CONFLICT)
    SCHEDULE_CONFLICT = (2004, "Конфликт расписания", status.HTTP_409_CONFLICT)
    
    # Кастомные ошибки платежей (3000-3999)
    STRIPE_PAYMENT_DECLINED = (3000, "Платеж отклонен банком", status.HTTP_400_BAD_REQUEST)
    STRIPE_CARD_EXPIRED = (3001, "Срок действия карты истек", status.HTTP_400_BAD_REQUEST)
    STRIPE_INSUFFICIENT_FUNDS = (3002, "Недостаточно средств на карте", status.HTTP_400_BAD_REQUEST)
    STRIPE_INVALID_CVC = (3003, "Неверный CVC код", status.HTTP_400_BAD_REQUEST)
    STRIPE_INVALID_CARD_NUMBER = (3004, "Неверный номер карты", status.HTTP_400_BAD_REQUEST)
    STRIPE_RATE_LIMIT_EXCEEDED = (3005, "Превышен лимит запросов к Stripe", status.HTTP_429_TOO_MANY_REQUESTS)
    STRIPE_SERVICE_UNAVAILABLE = (3006, "Сервис Stripe временно недоступен", status.HTTP_502_BAD_GATEWAY)
    WITHDRAWAL_MINIMUM_AMOUNT = (3007, "Сумма вывода меньше минимальной", status.HTTP_400_BAD_REQUEST)
    WITHDRAWAL_MAXIMUM_AMOUNT = (3008, "Сумма вывода больше максимальной", status.HTTP_400_BAD_REQUEST)
    WITHDRAWAL_INVALID_BANK_ACCOUNT = (3009, "Неверные данные банковского счета", status.HTTP_400_BAD_REQUEST)
    
    # Кастомные ошибки внешних сервисов (4000-4999)
    GOOGLE_CALENDAR_API_QUOTA_EXCEEDED = (4000, "Превышена квота Google Calendar API", status.HTTP_429_TOO_MANY_REQUESTS)
    GOOGLE_CALENDAR_SERVICE_UNAVAILABLE = (4001, "Google Calendar временно недоступен", status.HTTP_502_BAD_GATEWAY)
    GOOGLE_CALENDAR_INVALID_CREDENTIALS = (4002, "Неверные учетные данные Google Calendar", status.HTTP_401_UNAUTHORIZED)
    FIREBASE_AUTH_TOKEN_EXPIRED = (4003, "Токен Firebase истек", status.HTTP_401_UNAUTHORIZED)
    FIREBASE_INVALID_TOKEN = (4004, "Неверный токен Firebase", status.HTTP_401_UNAUTHORIZED)
    FIREBASE_SERVICE_UNAVAILABLE = (4005, "Firebase временно недоступен", status.HTTP_502_BAD_GATEWAY)
    EMAIL_SERVICE_SMTP_ERROR = (4006, "Ошибка SMTP сервера", status.HTTP_502_BAD_GATEWAY)
    EMAIL_SERVICE_INVALID_RECIPIENT = (4007, "Неверный адрес получателя", status.HTTP_400_BAD_REQUEST)
    
    # Кастомные ошибки файлов (5000-5999)
    FILE_SIZE_EXCEEDS_10MB = (5000, "Размер файла превышает 10MB", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    FILE_SIZE_EXCEEDS_50MB = (5001, "Размер файла превышает 50MB", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    FILE_TYPE_NOT_ALLOWED = (5002, "Тип файла не разрешен", status.HTTP_400_BAD_REQUEST)
    FILE_CORRUPTED = (5003, "Файл поврежден", status.HTTP_400_BAD_REQUEST)
    UPLOAD_QUOTA_EXCEEDED = (5004, "Превышена квота загрузки", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    FILE_TOO_LARGE = (5005, "Файл слишком большой", status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    INVALID_FILE_FORMAT = (5006, "Неверный формат файла", status.HTTP_400_BAD_REQUEST)
    FILE_PROCESSING_ERROR = (5007, "Ошибка обработки файла", status.HTTP_500_INTERNAL_SERVER_ERROR)
    FILE_UPLOAD_ERROR = (5008, "Ошибка загрузки файла", status.HTTP_500_INTERNAL_SERVER_ERROR)
    FILE_DELETE_ERROR = (5009, "Ошибка удаления файла", status.HTTP_500_INTERNAL_SERVER_ERROR)
    FILE_RETRIEVE_ERROR = (5010, "Ошибка получения файла", status.HTTP_500_INTERNAL_SERVER_ERROR)
    FILE_NOT_FOUND = (5011, "Файл не найден", status.HTTP_404_NOT_FOUND)
    FILE_STORAGE_ERROR = (5012, "Ошибка хранилища файлов", status.HTTP_500_INTERNAL_SERVER_ERROR)
    PROFILE_PHOTO_NOT_FOUND = (5013, "Фото профиля не найдено", status.HTTP_404_NOT_FOUND)
    
    # Кастомные ошибки приложения (6000+)
    MEETING_LINK_GENERATION_FAILED = (6000, "Не удалось создать ссылку для встречи", status.HTTP_500_INTERNAL_SERVER_ERROR)
    MEETING_ALREADY_EXISTS_SAME_TIME = (6001, "Встреча уже существует в это время", status.HTTP_409_CONFLICT)
    MEETING_TIME_IN_PAST = (6002, "Время встречи в прошлом", status.HTTP_400_BAD_REQUEST)
    MEETING_TIME_TOO_LATE = (6003, "Время встречи слишком поздно", status.HTTP_400_BAD_REQUEST)
    MEETING_DURATION_TOO_LONG = (6004, "Длительность встречи слишком большая", status.HTTP_400_BAD_REQUEST)
    MEETING_PARTICIPANTS_LIMIT_EXCEEDED = (6005, "Превышен лимит участников встречи", status.HTTP_400_BAD_REQUEST)
    
    # Кастомные ошибки workers (7000+)
    TASK_CANNOT_CANCEL = (7000, "Задача не может быть отменена", status.HTTP_400_BAD_REQUEST)
    TASK_NOT_FOUND = (7001, "Задача не найдена", status.HTTP_404_NOT_FOUND)
    TASK_ALREADY_COMPLETED = (7002, "Задача уже завершена", status.HTTP_400_BAD_REQUEST)
    
    def __init__(self, error_number, error_message, status_code):
        self.error_number = error_number
        self.error_message = error_message
        self.status_code = status_code
    
    @classmethod
    def get_by_number(cls, number):
        """Получить ошибку по номеру"""
        for error in cls:
            if error.error_number == number:
                return error
        return None
    
    @classmethod
    def get_by_name(cls, name):
        """Получить ошибку по имени"""
        try:
            return cls[name]
        except KeyError:
            return None 
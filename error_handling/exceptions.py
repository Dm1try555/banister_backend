from rest_framework.exceptions import APIException
from rest_framework import status


class BaseCustomException(APIException):
    """
    Базовый класс для всех кастомных исключений
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Произошла ошибка'
    default_code = 'error'

    def __init__(self, detail=None, code=None, error_number=None):
        super().__init__(detail, code)
        self.error_number = error_number or self.default_code


class ValidationError(BaseCustomException):
    """
    Ошибка валидации данных
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Ошибка валидации данных'
    default_code = 'VALIDATION_ERROR'


class AuthenticationError(BaseCustomException):
    """
    Ошибка аутентификации
    """
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Ошибка аутентификации'
    default_code = 'AUTHENTICATION_ERROR'


class PermissionError(BaseCustomException):
    """
    Ошибка прав доступа
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Недостаточно прав для выполнения операции'
    default_code = 'PERMISSION_ERROR'


class NotFoundError(BaseCustomException):
    """
    Ошибка - ресурс не найден
    """
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Запрашиваемый ресурс не найден'
    default_code = 'NOT_FOUND_ERROR'


class ConflictError(BaseCustomException):
    """
    Ошибка конфликта данных
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Конфликт данных'
    default_code = 'CONFLICT_ERROR'


class ServerError(BaseCustomException):
    """
    Внутренняя ошибка сервера
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Внутренняя ошибка сервера'
    default_code = 'SERVER_ERROR'


class DatabaseError(BaseCustomException):
    """
    Ошибка базы данных
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Ошибка базы данных'
    default_code = 'DATABASE_ERROR'


class ExternalServiceError(BaseCustomException):
    """
    Ошибка внешнего сервиса
    """
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'Ошибка внешнего сервиса'
    default_code = 'EXTERNAL_SERVICE_ERROR'


class RateLimitError(BaseCustomException):
    """
    Ошибка превышения лимита запросов
    """
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Превышен лимит запросов'
    default_code = 'RATE_LIMIT_ERROR'


# Специфичные ошибки для бизнес-логики
class UserNotFoundError(NotFoundError):
    default_detail = 'Пользователь не найден'
    default_code = 'USER_NOT_FOUND'


class InvalidCredentialsError(AuthenticationError):
    default_detail = 'Неверные учетные данные'
    default_code = 'INVALID_CREDENTIALS'


class EmailAlreadyExistsError(ConflictError):
    default_detail = 'Пользователь с таким email уже существует'
    default_code = 'EMAIL_ALREADY_EXISTS'


class InvalidVerificationCodeError(ValidationError):
    default_detail = 'Неверный код подтверждения'
    default_code = 'INVALID_VERIFICATION_CODE'


class ExpiredVerificationCodeError(ValidationError):
    default_detail = 'Код подтверждения истек'
    default_code = 'EXPIRED_VERIFICATION_CODE'


class BookingNotFoundError(NotFoundError):
    default_detail = 'Бронирование не найдено'
    default_code = 'BOOKING_NOT_FOUND'


class ServiceNotFoundError(NotFoundError):
    default_detail = 'Услуга не найдена'
    default_code = 'SERVICE_NOT_FOUND'


class ProviderNotFoundError(NotFoundError):
    default_detail = 'Поставщик услуг не найден'
    default_code = 'PROVIDER_NOT_FOUND'


class PaymentError(BaseCustomException):
    default_detail = 'Ошибка платежа'
    default_code = 'PAYMENT_ERROR'


class WithdrawalError(BaseCustomException):
    default_detail = 'Ошибка вывода средств'
    default_code = 'WITHDRAWAL_ERROR'


class InvalidEmailError(BaseCustomException):
    status_code = 400
    default_detail = 'Некорректный email'
    default_code = 'INVALID_EMAIL' 
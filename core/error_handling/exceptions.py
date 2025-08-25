from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from .enums import ErrorCode
from .utils import get_status_code_from_error_code


class CustomAPIException(APIException):
    """Базовое исключение для всех кастомных ошибок"""
    
    def __init__(self, error_code: ErrorCode, detail=None, status_code=None):
        self.error_code = error_code
        self.detail = detail or error_code.description
        self.status_code = status_code or get_status_code_from_error_code(error_code)
        super().__init__(detail=self.detail)


class AuthenticationError(CustomAPIException):
    """Ошибки аутентификации (401)"""
    def __init__(self, error_code: ErrorCode = ErrorCode.INVALID_CREDENTIALS, detail=None):
        super().__init__(error_code, detail)


class BookingError(CustomAPIException):
    """Ошибки бронирования (409)"""
    def __init__(self, error_code: ErrorCode = ErrorCode.BOOKING_NOT_FOUND, detail=None):
        super().__init__(error_code, detail)


class ServiceError(CustomAPIException):
    """Ошибки сервисов (404)"""
    def __init__(self, error_code: ErrorCode = ErrorCode.SERVICE_NOT_FOUND, detail=None):
        super().__init__(error_code, detail)


class PaymentError(CustomAPIException):
    """Ошибки платежей (402)"""
    def __init__(self, error_code: ErrorCode = ErrorCode.PAYMENT_FAILED, detail=None):
        super().__init__(error_code, detail)


class DocumentError(CustomAPIException):
    """Ошибки документов (400)"""
    def __init__(self, error_code: ErrorCode = ErrorCode.DOCUMENT_NOT_FOUND, detail=None):
        super().__init__(error_code, detail)


class ValidationError(CustomAPIException):
    """Ошибки валидации (422)"""
    def __init__(self, error_code: ErrorCode = ErrorCode.INVALID_DATA, detail=None):
        super().__init__(error_code, detail)


class SystemError(CustomAPIException):
    """Системные ошибки (500)"""
    def __init__(self, error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR, detail=None):
        super().__init__(error_code, detail)
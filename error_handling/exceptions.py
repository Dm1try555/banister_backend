from rest_framework.exceptions import APIException
from rest_framework import status


class BaseCustomException(APIException):
    """Base class for all custom exceptions"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An error occurred'
    default_code = 'error'

    def __init__(self, detail=None, code=None, error_number=None):
        super().__init__(detail, code)
        self.error_number = error_number or self.default_code


class ValidationError(BaseCustomException):
    """Data validation error"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Data validation error'
    default_code = 'VALIDATION_ERROR'


class AuthenticationError(BaseCustomException):
    """Authentication error"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication error'
    default_code = 'AUTHENTICATION_ERROR'


class CustomPermissionError(BaseCustomException):
    """Permission error"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Insufficient permissions to perform the operation'
    default_code = 'PERMISSION_ERROR'


class NotFoundError(BaseCustomException):
    """Resource not found error"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Requested resource not found'
    default_code = 'NOT_FOUND_ERROR'


class ConflictError(BaseCustomException):
    """Data conflict error"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Data conflict'
    default_code = 'CONFLICT_ERROR'


class ServerError(BaseCustomException):
    """Internal server error"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Internal server error'
    default_code = 'SERVER_ERROR'


class DatabaseError(BaseCustomException):
    """Database error"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Database error'
    default_code = 'DATABASE_ERROR'


class ExternalServiceError(BaseCustomException):
    """External service error"""
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'External service error'
    default_code = 'EXTERNAL_SERVICE_ERROR'


class RateLimitError(BaseCustomException):
    """Rate limit exceeded error"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded'
    default_code = 'RATE_LIMIT_ERROR'


# Business logic specific errors
class UserNotFoundError(NotFoundError):
    default_detail = 'User not found'
    default_code = 'USER_NOT_FOUND'


class InvalidCredentialsError(AuthenticationError):
    default_detail = 'Invalid credentials'
    default_code = 'INVALID_CREDENTIALS'


class EmailAlreadyExistsError(ConflictError):
    default_detail = 'A user with this email already exists'
    default_code = 'EMAIL_ALREADY_EXISTS'


class InvalidVerificationCodeError(ValidationError):
    default_detail = 'Invalid verification code'
    default_code = 'INVALID_VERIFICATION_CODE'


class ExpiredVerificationCodeError(ValidationError):
    default_detail = 'Verification code expired'
    default_code = 'EXPIRED_VERIFICATION_CODE'


class BookingNotFoundError(NotFoundError):
    default_detail = 'Booking not found'
    default_code = 'BOOKING_NOT_FOUND'


class ServiceNotFoundError(NotFoundError):
    default_detail = 'Service not found'
    default_code = 'SERVICE_NOT_FOUND'


class ProviderNotFoundError(NotFoundError):
    default_detail = 'Provider not found'
    default_code = 'PROVIDER_NOT_FOUND'


class PaymentError(BaseCustomException):
    default_detail = 'Payment error'
    default_code = 'PAYMENT_ERROR'


class WithdrawalError(BaseCustomException):
    default_detail = 'Withdrawal error'
    default_code = 'WITHDRAWAL_ERROR'


class InvalidEmailError(BaseCustomException):
    status_code = 400
    default_detail = 'Invalid email'
    default_code = 'INVALID_EMAIL' 
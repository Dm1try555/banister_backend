from rest_framework.exceptions import APIException
from .enums import ErrorCode


class CustomAPIException(APIException):
    def __init__(self, error_code: ErrorCode, detail=None):
        self.error_code = error_code
        self.status_code = self._get_status_code(error_code)
        
        if detail is None:
            detail = error_code.description
            
        super().__init__(detail)
    
    def _get_status_code(self, error_code: ErrorCode):
        # Map error types to HTTP status codes
        code_ranges = {
            range(1000, 2000): 401,  # Authentication errors -> 401 Unauthorized
            range(2000, 3000): 409,  # Booking errors -> 409 Conflict
            range(3000, 4000): 404,  # Service errors -> 404 Not Found
            range(4000, 4500): 402,  # Payment errors -> 402 Payment Required
            range(4500, 5000): 404,  # Document errors -> 404 Not Found
            range(5000, 6000): 400,  # Withdrawal errors -> 400 Bad Request
            range(6000, 7000): 404,  # Notification errors -> 404 Not Found
            range(7000, 8000): 403,  # Chat/Message errors -> 403 Forbidden
            range(8000, 9000): 409,  # Schedule errors -> 409 Conflict
            range(9000, 9900): 400,  # Validation errors -> 400 Bad Request
            range(9900, 10000): 500, # System errors -> 500 Internal Server Error
        }
        
        for code_range, status_code in code_ranges.items():
            if error_code.code in code_range:
                return status_code
        
        return 400  # Default to Bad Request


class AuthenticationError(CustomAPIException):
    pass


class BookingError(CustomAPIException):
    pass


class ServiceError(CustomAPIException):
    pass


class PaymentError(CustomAPIException):
    pass


class ValidationError(CustomAPIException):
    pass


class SystemError(CustomAPIException):
    pass
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
        code_ranges = {
            range(1000, 2000): 401,
            range(2000, 3000): 409,
            range(3000, 4000): 404,
            range(4000, 4500): 402,
            range(4500, 5000): 404,
            range(5000, 6000): 400,
            range(6000, 7000): 404,
            range(7000, 8000): 403,
            range(8000, 9000): 409,
            range(9000, 9900): 400,
            range(9900, 10000): 500,
        }
        
        for code_range, status_code in code_ranges.items():
            if error_code.code in code_range:
                return status_code
        
        return 400


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
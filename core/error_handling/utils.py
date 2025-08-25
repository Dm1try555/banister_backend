from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from .enums import ErrorCode


def get_status_code_from_error_code(error_code: ErrorCode) -> int:
    """Determines HTTP status code based on ErrorCode"""
    if error_code.code in range(1000, 2000):
        return status.HTTP_401_UNAUTHORIZED
    elif error_code.code in range(2000, 3000):
        return status.HTTP_409_CONFLICT
    elif error_code.code in range(3000, 4000):
        return status.HTTP_404_NOT_FOUND
    elif error_code.code in range(4000, 4500):
        return status.HTTP_402_PAYMENT_REQUIRED
    elif error_code.code in range(4500, 5000):
        return status.HTTP_400_BAD_REQUEST
    elif error_code.code in range(5000, 6000):
        return status.HTTP_400_BAD_REQUEST
    elif error_code.code in range(6000, 7000):
        return status.HTTP_404_NOT_FOUND
    elif error_code.code in range(7000, 8000):
        return status.HTTP_403_FORBIDDEN
    elif error_code.code in range(8000, 9000):
        return status.HTTP_409_CONFLICT
    elif error_code.code in range(9000, 10000):
        return status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        return status.HTTP_400_BAD_REQUEST


def create_error_response(error_code: ErrorCode = None, detail=None, status_code=None, request=None):
    """Creates a standardized error response"""
    if error_code is None:
        # For standard DRF errors without ErrorCode
        if status_code is None:
            status_code = status.HTTP_400_BAD_REQUEST
        
        message = detail or "An error occurred"
        error_title = "Error"
        error_code_num = status_code
    else:
        # For our custom errors with ErrorCode
        if status_code is None:
            status_code = get_status_code_from_error_code(error_code)
        
        message = f"{error_code.code}: {detail or error_code.description}"
        error_title = error_code.title
        error_code_num = error_code.code
    
    exception_type_map = {
        400: "BadRequestException",
        401: "UnauthorizedException", 
        402: "PaymentRequiredException",
        403: "ForbiddenException",
        404: "NotFoundException",
        409: "ConflictException",
        422: "ValidationException",
        500: "InternalServerException"
    }
    exception_type = exception_type_map.get(status_code, "APIException")
    
    error_response = {
        "statusCode": status_code,
        "errorCode": error_code_num,
        "exceptionType": exception_type,
        "message": message,
        "error": error_title,
        "timestamp": now().isoformat(),
        "endpoint": request.path if request else "",
        "method": request.method if request else ""
    }
    
    return Response(error_response, status=status_code)


def create_success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Создает стандартизированный успешный ответ
    
    Args:
        data: Данные для ответа
        message: Сообщение об успехе
        status_code: HTTP статус код
    
    Returns:
        Response с успешным результатом
    """
    response_data = {
        'success': True,
        "message": message
    }
    
    if data is not None:
        response_data['data'] = data
    
    return Response(response_data, status=status_code)


def handle_validation_error(validation_errors, request=None):
    """
    Простая функция для обработки ошибок валидации
    Автоматически определяет код ошибки из сообщения
    """
    error_text = str(validation_errors)
    
    # Если сообщение уже содержит код ошибки (например: "1012: Passwords do not match")
    if ':' in error_text and error_text.split(':')[0].strip().isdigit():
        error_code_num = int(error_text.split(':')[0].strip())
        
        # Находим ErrorCode по номеру
        for error_code in ErrorCode:
            if error_code.code == error_code_num:
                return create_error_response(error_code, error_text, request=request)
    
    # Если код не найден, используем общий код
    return create_error_response(ErrorCode.INVALID_DATA, error_text, request=request) 
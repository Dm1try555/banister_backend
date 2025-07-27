# Система обработки ошибок

Эта система предоставляет стандартизированную обработку ошибок для Django REST Framework API с поддержкой error_number и error_message.

## Структура ответов

### Успешный ответ
```json
{
    "success": true,
    "message": "Операция выполнена успешно",
    "data": {
        // данные ответа
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

### Ответ с ошибкой
```json
{
    "success": false,
    "error": {
        "error_number": "VALIDATION_ERROR",
        "error_message": "Ошибка валидации данных",
        "timestamp": "2024-01-01T12:00:00Z"
    }
}
```

### Ответ с ошибками валидации полей
```json
{
    "success": false,
    "error": {
        "error_number": "VALIDATION_ERROR",
        "error_message": "Ошибка валидации данных",
        "field_errors": {
            "email": "Это поле обязательно",
            "password": "Пароль должен содержать минимум 8 символов"
        },
        "timestamp": "2024-01-01T12:00:00Z"
    }
}
```

## Доступные исключения

### Базовые исключения
- `ValidationError` - Ошибка валидации данных (400)
- `AuthenticationError` - Ошибка аутентификации (401)
- `PermissionError` - Ошибка прав доступа (403)
- `NotFoundError` - Ресурс не найден (404)
- `ConflictError` - Конфликт данных (409)
- `ServerError` - Внутренняя ошибка сервера (500)
- `DatabaseError` - Ошибка базы данных (500)
- `ExternalServiceError` - Ошибка внешнего сервиса (502)
- `RateLimitError` - Превышение лимита запросов (429)

### Специфичные исключения
- `UserNotFoundError` - Пользователь не найден
- `InvalidCredentialsError` - Неверные учетные данные
- `EmailAlreadyExistsError` - Email уже существует
- `InvalidVerificationCodeError` - Неверный код подтверждения
- `ExpiredVerificationCodeError` - Код подтверждения истек
- `BookingNotFoundError` - Бронирование не найдено
- `ServiceNotFoundError` - Услуга не найдена
- `ProviderNotFoundError` - Поставщик услуг не найден
- `PaymentError` - Ошибка платежа
- `WithdrawalError` - Ошибка вывода средств

## Использование

### 1. Базовый View класс

```python
from error_handling.views import BaseAPIView
from error_handling.exceptions import UserNotFoundError

class MyView(BaseAPIView):
    def get(self, request):
        try:
            # ваша логика
            return self.success_response(
                data={'result': 'success'},
                message='Операция выполнена успешно'
            )
        except User.DoesNotExist:
            raise UserNotFoundError('Пользователь не найден')
```

### 2. Использование исключений

```python
from error_handling.exceptions import (
    ValidationError, AuthenticationError, NotFoundError
)

# Вызов исключения
raise ValidationError('Неверные данные')

# С кастомным сообщением
raise NotFoundError('Запрашиваемый ресурс не найден')

# С кастомным error_number
raise ValidationError('Неверные данные', error_number='CUSTOM_VALIDATION_ERROR')
```

### 3. Создание ответов вручную

```python
from error_handling.utils import create_error_response, create_success_response

# Создание ответа с ошибкой
return create_error_response(
    error_number='CUSTOM_ERROR',
    error_message='Описание ошибки',
    status_code=400
)

# Создание успешного ответа
return create_success_response(
    data={'result': 'success'},
    message='Операция выполнена'
)
```

### 4. Обработка ошибок валидации

```python
from error_handling.utils import format_validation_errors

class MyView(BaseAPIView):
    def post(self, request):
        serializer = MySerializer(data=request.data)
        if not serializer.is_valid():
            field_errors = format_validation_errors(serializer.errors)
            return self.validation_error_response(field_errors)
        
        # ваша логика
        return self.success_response(data=serializer.data)
```

### 5. Декоратор для обработки исключений

```python
from error_handling.utils import handle_exception

class MyView(BaseAPIView):
    @handle_exception
    def get(self, request):
        # ваша логика
        return self.success_response(data={'result': 'success'})
```

## Тестирование

Для тестирования системы обработки ошибок доступен специальный endpoint:

### GET /api/v1/error-test/
Возвращает успешный ответ для проверки формата.

### POST /api/v1/error-test/
Тестирует различные типы ошибок. Отправьте JSON с полем `error_type`:

```json
{
    "error_type": "validation"
}
```

Доступные типы ошибок:
- `validation` - Ошибка валидации
- `authentication` - Ошибка аутентификации
- `not_found` - Ресурс не найден
- `server` - Ошибка сервера

## Настройка

### 1. Добавление в INSTALLED_APPS
```python
INSTALLED_APPS = [
    # ...
    'error_handling',
    # ...
]
```

### 2. Добавление middleware
```python
MIDDLEWARE = [
    # ...
    'error_handling.middleware.ErrorHandlingMiddleware',
]
```

### 3. Настройка DRF exception handler
```python
REST_FRAMEWORK = {
    # ...
    'EXCEPTION_HANDLER': 'error_handling.middleware.custom_exception_handler',
}
```

## Логирование

Система автоматически логирует все ошибки. Для настройки логирования добавьте в settings.py:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'error_handling.log',
        },
    },
    'loggers': {
        'error_handling': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

## Миграция существующих views

Для миграции существующих views:

1. Замените `APIView` на `BaseAPIView`
2. Замените `Response` на `self.success_response()` или `self.error_response()`
3. Замените стандартные исключения на кастомные из `error_handling.exceptions`
4. Обновите обработку ошибок валидации

Пример миграции:

```python
# Было
class MyView(APIView):
    def get(self, request):
        try:
            user = User.objects.get(id=1)
            return Response({'user': user.name})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

# Стало
class MyView(BaseAPIView):
    def get(self, request):
        try:
            user = User.objects.get(id=1)
            return self.success_response(data={'user': user.name})
        except User.DoesNotExist:
            raise UserNotFoundError('Пользователь не найден')
``` 
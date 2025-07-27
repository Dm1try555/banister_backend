# Руководство по миграции на систему обработки ошибок

Это руководство поможет вам мигрировать существующие views на новую систему обработки ошибок.

## Шаг 1: Подготовка

Убедитесь, что система обработки ошибок подключена в `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'error_handling',
    # ...
]

MIDDLEWARE = [
    # ...
    'error_handling.middleware.ErrorHandlingMiddleware',
]

REST_FRAMEWORK = {
    # ...
    'EXCEPTION_HANDLER': 'error_handling.middleware.custom_exception_handler',
}
```

## Шаг 2: Импорты

Добавьте необходимые импорты в начало файла views:

```python
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    ValidationError, AuthenticationError, PermissionError, NotFoundError,
    ConflictError, ServerError, UserNotFoundError, EmailAlreadyExistsError
)
from error_handling.utils import format_validation_errors
```

## Шаг 3: Замена базового класса

Замените `APIView` на `BaseAPIView`:

```python
# Было
class MyView(APIView):
    pass

# Стало
class MyView(BaseAPIView):
    pass
```

## Шаг 4: Обновление методов

### 4.1 Успешные ответы

```python
# Было
return Response({'data': result}, status=200)

# Стало
return self.success_response(
    data=result,
    message='Операция выполнена успешно'
)
```

### 4.2 Ответы с ошибками

```python
# Было
return Response({'error': 'User not found'}, status=404)

# Стало
raise UserNotFoundError('Пользователь не найден')
```

### 4.3 Обработка валидации

```python
# Было
if not serializer.is_valid():
    return Response(serializer.errors, status=400)

# Стало
if not serializer.is_valid():
    field_errors = format_validation_errors(serializer.errors)
    return self.validation_error_response(field_errors)
```

## Шаг 5: Обработка исключений

### 5.1 Стандартные исключения Django

```python
# Было
try:
    user = User.objects.get(id=user_id)
except User.DoesNotExist:
    return Response({'error': 'User not found'}, status=404)

# Стало
try:
    user = User.objects.get(id=user_id)
except User.DoesNotExist:
    raise UserNotFoundError('Пользователь не найден')
```

### 5.2 Кастомные исключения

```python
# Было
if user.role != 'admin':
    return Response({'error': 'Permission denied'}, status=403)

# Стало
if user.role != 'admin':
    raise PermissionError('Недостаточно прав для выполнения операции')
```

## Примеры миграции

### Пример 1: Простой view

```python
# Было
class UserView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

# Стало
class UserView(BaseAPIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            return self.success_response(
                data={
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                message='Пользователь найден'
            )
        except User.DoesNotExist:
            raise UserNotFoundError('Пользователь не найден')
```

### Пример 2: View с валидацией

```python
# Было
class CreateUserView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        try:
            user = serializer.save()
            return Response({
                'id': user.id,
                'message': 'User created successfully'
            }, status=201)
        except IntegrityError:
            return Response({'error': 'Email already exists'}, status=409)

# Стало
class CreateUserView(BaseAPIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            field_errors = format_validation_errors(serializer.errors)
            return self.validation_error_response(field_errors)
        
        try:
            user = serializer.save()
            return self.success_response(
                data={'id': user.id},
                message='Пользователь создан успешно'
            )
        except IntegrityError:
            raise EmailAlreadyExistsError('Пользователь с таким email уже существует')
```

### Пример 3: View с бизнес-логикой

```python
# Было
class BookingView(APIView):
    def post(self, request):
        if request.user.role != 'customer':
            return Response({'error': 'Only customers can create bookings'}, status=403)
        
        serializer = BookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        # Проверка доступности времени
        booking_date = serializer.validated_data.get('booking_date')
        booking_time = serializer.validated_data.get('booking_time')
        
        if Booking.objects.filter(
            booking_date=booking_date,
            booking_time=booking_time,
            status='confirmed'
        ).exists():
            return Response({'error': 'Time slot is already booked'}, status=409)
        
        booking = serializer.save(customer=request.user)
        return Response({
            'id': booking.id,
            'message': 'Booking created successfully'
        }, status=201)

# Стало
class BookingView(BaseAPIView):
    def post(self, request):
        if request.user.role != 'customer':
            raise PermissionError('Только клиенты могут создавать бронирования')
        
        serializer = BookingSerializer(data=request.data)
        if not serializer.is_valid():
            field_errors = format_validation_errors(serializer.errors)
            return self.validation_error_response(field_errors)
        
        # Проверка доступности времени
        booking_date = serializer.validated_data.get('booking_date')
        booking_time = serializer.validated_data.get('booking_time')
        
        if Booking.objects.filter(
            booking_date=booking_date,
            booking_time=booking_time,
            status='confirmed'
        ).exists():
            raise ConflictError('Выбранное время уже занято')
        
        booking = serializer.save(customer=request.user)
        return self.success_response(
            data={'id': booking.id},
            message='Бронирование создано успешно'
        )
```

## Шаг 6: Тестирование

После миграции протестируйте все endpoints:

1. Проверьте успешные ответы
2. Проверьте ответы с ошибками
3. Проверьте валидацию данных
4. Проверьте обработку исключений

Используйте тестовый endpoint: `GET /api/v1/error-test/`

## Шаг 7: Обновление документации

Обновите документацию API, чтобы отразить новую структуру ответов.

## Полезные советы

1. **Постепенная миграция**: Мигрируйте views по одному, тестируя каждый
2. **Логирование**: Используйте логирование для отслеживания ошибок
3. **Консистентность**: Используйте одинаковые error_number для похожих ошибок
4. **Документация**: Обновляйте документацию по мере миграции

## Проверка миграции

После миграции проверьте:

- [ ] Все успешные ответы используют `self.success_response()`
- [ ] Все ошибки используют кастомные исключения
- [ ] Валидация использует `self.validation_error_response()`
- [ ] Логирование работает корректно
- [ ] Документация обновлена 
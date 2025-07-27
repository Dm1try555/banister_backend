"""
Примеры использования системы обработки ошибок

Этот файл содержит примеры того, как использовать систему обработки ошибок
в различных сценариях разработки.
"""

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.db import IntegrityError

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    ValidationError, AuthenticationError, PermissionError, NotFoundError,
    ConflictError, ServerError, UserNotFoundError, EmailAlreadyExistsError
)
from error_handling.utils import (
    create_error_response, create_success_response, 
    format_validation_errors, handle_exception
)


# Пример 1: Простой view с обработкой ошибок
class SimpleExampleView(BaseAPIView):
    """
    Простой пример использования BaseAPIView
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Пример успешного ответа
        """
        return self.success_response(
            data={'message': 'Hello World'},
            message='Запрос выполнен успешно'
        )
    
    def post(self, request):
        """
        Пример обработки ошибок
        """
        try:
            user_id = request.data.get('user_id')
            
            if not user_id:
                return self.error_response(
                    error_number='MISSING_USER_ID',
                    error_message='ID пользователя не указан',
                    status_code=400
                )
            
            user = User.objects.get(id=user_id)
            
            return self.success_response(
                data={'user': {'id': user.id, 'username': user.username}},
                message='Пользователь найден'
            )
            
        except User.DoesNotExist:
            raise UserNotFoundError('Пользователь не найден')
        except Exception as e:
            return self.error_response(
                error_number='UNKNOWN_ERROR',
                error_message=f'Произошла ошибка: {str(e)}',
                status_code=500
            )


# Пример 2: Обработка валидации данных
class ValidationExampleView(BaseAPIView):
    """
    Пример обработки валидации данных
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Пример валидации данных с детальными ошибками
        """
        # Имитация валидации
        errors = {}
        
        email = request.data.get('email')
        password = request.data.get('password')
        age = request.data.get('age')
        
        if not email:
            errors['email'] = 'Email обязателен'
        elif '@' not in email:
            errors['email'] = 'Неверный формат email'
        
        if not password:
            errors['password'] = 'Пароль обязателен'
        elif len(password) < 8:
            errors['password'] = 'Пароль должен содержать минимум 8 символов'
        
        if age:
            try:
                age_int = int(age)
                if age_int < 18:
                    errors['age'] = 'Возраст должен быть не менее 18 лет'
            except ValueError:
                errors['age'] = 'Возраст должен быть числом'
        
        if errors:
            return self.validation_error_response(errors)
        
        return self.success_response(
            data={'email': email, 'age': age},
            message='Данные валидны'
        )


# Пример 3: Использование исключений
class ExceptionExampleView(BaseAPIView):
    """
    Пример использования различных типов исключений
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Пример различных типов ошибок
        """
        error_type = request.query_params.get('error_type', 'validation')
        
        if error_type == 'validation':
            raise ValidationError('Ошибка валидации данных')
        elif error_type == 'authentication':
            raise AuthenticationError('Ошибка аутентификации')
        elif error_type == 'permission':
            raise PermissionError('Недостаточно прав')
        elif error_type == 'not_found':
            raise NotFoundError('Ресурс не найден')
        elif error_type == 'conflict':
            raise ConflictError('Конфликт данных')
        elif error_type == 'server':
            raise ServerError('Внутренняя ошибка сервера')
        else:
            return self.success_response(
                data={'message': 'Нет ошибок'},
                message='Запрос выполнен успешно'
            )


# Пример 4: Декоратор для обработки исключений
class DecoratorExampleView(BaseAPIView):
    """
    Пример использования декоратора @handle_exception
    """
    permission_classes = [AllowAny]
    
    @handle_exception
    def get(self, request):
        """
        Метод с автоматической обработкой исключений
        """
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            raise ValidationError('ID пользователя не указан')
        
        user = User.objects.get(id=user_id)
        
        return self.success_response(
            data={'user': {'id': user.id, 'username': user.username}},
            message='Пользователь найден'
        )


# Пример 5: Создание ответов вручную
class ManualResponseExampleView(APIView):
    """
    Пример создания ответов вручную без BaseAPIView
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Пример успешного ответа
        """
        return create_success_response(
            data={'message': 'Manual success response'},
            message='Ручной успешный ответ'
        )
    
    def post(self, request):
        """
        Пример ответа с ошибкой
        """
        return create_error_response(
            error_number='MANUAL_ERROR',
            error_message='Ручная ошибка',
            status_code=400
        )


# Пример 6: Обработка ошибок базы данных
class DatabaseExampleView(BaseAPIView):
    """
    Пример обработки ошибок базы данных
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Пример обработки IntegrityError
        """
        try:
            # Попытка создать пользователя с существующим email
            user = User.objects.create_user(
                username='test_user',
                email='existing@example.com',  # Предполагаем, что такой email уже существует
                password='testpass123'
            )
            
            return self.success_response(
                data={'user_id': user.id},
                message='Пользователь создан'
            )
            
        except IntegrityError:
            raise EmailAlreadyExistsError('Пользователь с таким email уже существует')
        except Exception as e:
            return self.error_response(
                error_number='DATABASE_ERROR',
                error_message=f'Ошибка базы данных: {str(e)}',
                status_code=500
            )


# Пример 7: Сложная бизнес-логика
class BusinessLogicExampleView(BaseAPIView):
    """
    Пример сложной бизнес-логики с обработкой ошибок
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Пример сложной бизнес-логики
        """
        try:
            # Получение данных
            amount = request.data.get('amount')
            service_id = request.data.get('service_id')
            
            # Валидация входных данных
            if not amount or not service_id:
                return self.error_response(
                    error_number='MISSING_REQUIRED_FIELDS',
                    error_message='Не указаны обязательные поля: amount, service_id',
                    status_code=400
                )
            
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError('Сумма должна быть положительной')
            except ValueError:
                return self.error_response(
                    error_number='INVALID_AMOUNT',
                    error_message='Неверная сумма',
                    status_code=400
                )
            
            # Проверка прав доступа
            if request.user.role not in ['customer', 'provider']:
                raise PermissionError('Недостаточно прав для выполнения операции')
            
            # Проверка лимитов
            if amount > 10000:
                return self.error_response(
                    error_number='AMOUNT_LIMIT_EXCEEDED',
                    error_message='Превышен лимит суммы (максимум 10000)',
                    status_code=400
                )
            
            # Имитация бизнес-логики
            if amount > 5000 and request.user.role == 'customer':
                # Требуется дополнительная проверка для крупных сумм
                return self.error_response(
                    error_number='LARGE_AMOUNT_REQUIRES_APPROVAL',
                    error_message='Для сумм более 5000 требуется дополнительная проверка',
                    status_code=400
                )
            
            # Успешное выполнение
            return self.success_response(
                data={
                    'amount': amount,
                    'service_id': service_id,
                    'user_id': request.user.id,
                    'status': 'approved'
                },
                message='Операция выполнена успешно'
            )
            
        except PermissionError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='BUSINESS_LOGIC_ERROR',
                error_message=f'Ошибка бизнес-логики: {str(e)}',
                status_code=500
            )


# Пример 8: Обработка внешних API
class ExternalAPIExampleView(BaseAPIView):
    """
    Пример обработки ошибок внешних API
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Пример обработки ошибок внешних сервисов
        """
        try:
            # Имитация запроса к внешнему API
            import requests
            from error_handling.exceptions import ExternalServiceError
            
            try:
                response = requests.get('https://api.example.com/data', timeout=5)
                response.raise_for_status()
                
                return self.success_response(
                    data=response.json(),
                    message='Данные получены от внешнего API'
                )
                
            except requests.exceptions.Timeout:
                raise ExternalServiceError('Внешний сервис не отвечает (таймаут)')
            except requests.exceptions.ConnectionError:
                raise ExternalServiceError('Ошибка подключения к внешнему сервису')
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    raise NotFoundError('Данные не найдены во внешнем сервисе')
                elif e.response.status_code == 401:
                    raise AuthenticationError('Ошибка аутентификации с внешним сервисом')
                else:
                    raise ExternalServiceError(f'Ошибка внешнего сервиса: {e.response.status_code}')
                    
        except (ExternalServiceError, NotFoundError, AuthenticationError):
            raise
        except Exception as e:
            return self.error_response(
                error_number='EXTERNAL_API_ERROR',
                error_message=f'Ошибка работы с внешним API: {str(e)}',
                status_code=500
            ) 
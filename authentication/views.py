from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer, QuickRegisterRequestSerializer, QuickRegisterVerifySerializer
from .firebase_auth import verify_firebase_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, VerificationCode, Profile, EmailConfirmationCode
import random
from rest_framework_simplejwt.tokens import RefreshToken

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    UserNotFoundError, InvalidCredentialsError, EmailAlreadyExistsError,
    InvalidVerificationCodeError, ExpiredVerificationCodeError, BaseCustomException
)
from error_handling.utils import ErrorResponseMixin, format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import api_view, permission_classes
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
import uuid

# --- Регистрация ---
@swagger_auto_schema(
    method='post',
    operation_description="Регистрация клиента (customer)",
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response('Успешная регистрация', UserSerializer),
        400: 'Ошибка валидации или пользователь уже существует'
    },
    tags=['Регистрация']
)
@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def register_customer(request):
    serializer = RegisterSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save(role='customer')
        return Response(serializer.data, status=201)
    except Exception as exc:
        from rest_framework.exceptions import ValidationError as DRFValidationError
        if isinstance(exc, DRFValidationError) or hasattr(exc, 'detail'):
            errors = exc.detail if hasattr(exc, 'detail') else exc.args[0]
            if isinstance(errors, dict) and 'email' in errors:
                email_errors = errors['email']
                if any('valid email address' in str(e) or 'Некорректный email' in str(e) for e in (email_errors if isinstance(email_errors, list) else [email_errors])):
                    return Response({
                        'success': False,
                        'error': {
                            'error_number': 'INVALID_EMAIL',
                            'error_message': 'Некорректный email',
                        }
                    }, status=400)
                if any('уже существует' in str(e) or 'already exists' in str(e) for e in (email_errors if isinstance(email_errors, list) else [email_errors])):
                    return Response({
                        'success': False,
                        'error': {
                            'error_number': 'EMAIL_ALREADY_EXISTS',
                            'error_message': 'Пользователь с таким email уже существует',
                        }
                    }, status=400)
            return Response({'success': False, 'error': errors}, status=400)
        raise

@swagger_auto_schema(
    method='post',
    operation_description="Регистрация провайдера (provider)",
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response('Успешная регистрация', UserSerializer),
        400: 'Ошибка валидации или пользователь уже существует'
    },
    tags=['Регистрация']
)
@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def register_provider(request):
    serializer = RegisterSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save(role='provider')
        return Response(serializer.data, status=201)
    except Exception as exc:
        from rest_framework.exceptions import ValidationError as DRFValidationError
        if isinstance(exc, DRFValidationError) or hasattr(exc, 'detail'):
            errors = exc.detail if hasattr(exc, 'detail') else exc.args[0]
            if isinstance(errors, dict) and 'email' in errors:
                email_errors = errors['email']
                if any('valid email address' in str(e) or 'Некорректный email' in str(e) for e in (email_errors if isinstance(email_errors, list) else [email_errors])):
                    return Response({
                        'success': False,
                        'error': {
                            'error_number': 'INVALID_EMAIL',
                            'error_message': 'Некорректный email',
                        }
                    }, status=400)
                if any('уже существует' in str(e) or 'already exists' in str(e) for e in (email_errors if isinstance(email_errors, list) else [email_errors])):
                    return Response({
                        'success': False,
                        'error': {
                            'error_number': 'EMAIL_ALREADY_EXISTS',
                            'error_message': 'Пользователь с таким email уже существует',
                        }
                    }, status=400)
            return Response({'success': False, 'error': errors}, status=400)
        raise

@swagger_auto_schema(
    method='post',
    operation_description="Регистрация менеджера (management)",
    request_body=RegisterSerializer,
    responses={
        201: openapi.Response('Успешная регистрация', UserSerializer),
        400: 'Ошибка валидации или пользователь уже существует'
    },
    tags=['Регистрация']
)
@transaction.atomic
@api_view(['POST'])
@permission_classes([AllowAny])
def register_management(request):
    serializer = RegisterSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save(role='management')
        return Response(serializer.data, status=201)
    except Exception as exc:
        from rest_framework.exceptions import ValidationError as DRFValidationError
        if isinstance(exc, DRFValidationError) or hasattr(exc, 'detail'):
            errors = exc.detail if hasattr(exc, 'detail') else exc.args[0]
            if isinstance(errors, dict) and 'email' in errors:
                email_errors = errors['email']
                if any('valid email address' in str(e) or 'Некорректный email' in str(e) for e in (email_errors if isinstance(email_errors, list) else [email_errors])):
                    return Response({
                        'success': False,
                        'error': {
                            'error_number': 'INVALID_EMAIL',
                            'error_message': 'Некорректный email',
                        }
                    }, status=400)
                if any('уже существует' in str(e) or 'already exists' in str(e) for e in (email_errors if isinstance(email_errors, list) else [email_errors])):
                    return Response({
                        'success': False,
                        'error': {
                            'error_number': 'EMAIL_ALREADY_EXISTS',
                            'error_message': 'Пользователь с таким email уже существует',
                        }
                    }, status=400)
            return Response({'success': False, 'error': errors}, status=400)
        raise

class FirebaseAuthView(BaseAPIView):
    permission_classes = [AllowAny]
    
    @transaction.atomic
    def post(self, request, provider):
        id_token = request.data.get('id_token')
        role = request.data.get('role', 'customer')
        
        if not id_token:
            from error_handling.exceptions import ValidationError
            raise ValidationError('Токен не предоставлен')
        
        decoded_token = verify_firebase_token(id_token)
        
        email = decoded_token.get('email')
        uid = decoded_token.get('uid')
        
        if not email:
            from error_handling.exceptions import ValidationError
            raise ValidationError('Недействительный токен')
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'role': role,
                'password_hash': uid
            }
        )
        
        if created:
            Profile.objects.create(user=user)
            if user.role == 'provider':
                from providers.models import Provider
                Provider.objects.create(user=user)
        
        token = CustomTokenObtainPairSerializer.get_token(user)
        
        return self.success_response(
            data={
                'access': str(token.access_token),
                'refresh': str(token),
                'role': user.role
            },
            message='Успешная аутентификация через Firebase'
        )

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# --- Профиль ---
@swagger_auto_schema(
    operation_description="Получить и обновить профиль пользователя",
    tags=['Профиль']
)
class ProfileView(BaseAPIView,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# --- Пароль ---
@swagger_auto_schema(
    operation_description="Сброс пароля пользователя по email",
    tags=['Пароль']
)
class PasswordResetView(BaseAPIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        return self.error_response(
            error_number='NOT_IMPLEMENTED',
            error_message='Сброс пароля не реализован',
            status_code=501
        )

@swagger_auto_schema(
    method='post',
    operation_description="Выход пользователя (logout)",
    responses={200: 'Выход выполнен успешно'},
    tags=['Авторизация']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    return Response({'success': True, 'message': 'Выход выполнен успешно'})

class VerificationCodeSenderMixin:
    """
    Миксин для отправки кода подтверждения по email или телефону.
    """
    serializer_class = None
    user_check_required = False

    def send_code(self, email, phone):
        code = str(random.randint(100000, 999999))
        VerificationCode.objects.create(email=email, phone=phone, code=code)
        # Здесь должна быть отправка email/SMS
        return code

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            
            if self.user_check_required:
                if not User.objects.filter(email=email) and not User.objects.filter(phone=phone):
                    raise UserNotFoundError('Пользователь не найден')
            
            code = self.send_code(email, phone)
            
            return self.success_response(
                data={'code': code},  # В продакшене убрать код
                message='Код подтверждения отправлен'
            )
            
        except BaseCustomException:
            raise
        except Exception as e:
            return self.error_response(
                error_number='CODE_SEND_ERROR',
                error_message=f'Ошибка отправки кода: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerificationCodeVerifyMixin:
    """
    Миксин для проверки кода подтверждения и выдачи токена.
    """
    serializer_class = None
    create_user_if_not_exists = False

    def verify_code(self, email, phone, code):
        try:
            vcode = VerificationCode.objects.filter(
                email=email, 
                phone=phone, 
                code=code, 
                is_used=False
            ).latest('created_at')
            
            # Проверка на истечение кода (например, 10 минут)
            from django.utils import timezone
            from datetime import timedelta
            
            if vcode.created_at < timezone.now() - timedelta(minutes=10):
                raise ExpiredVerificationCodeError('Код подтверждения истек')
            
            vcode.is_used = True
            vcode.save()
            
            return vcode
            
        except VerificationCode.DoesNotExist:
            raise InvalidVerificationCodeError('Неверный код подтверждения')

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            code = serializer.validated_data.get('code')
            
            vcode = self.verify_code(email, phone, code)
            
            if self.create_user_if_not_exists:
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': email.split('@')[0] if email else f'user_{phone}',
                        'role': 'customer'
                    }
                )
                
                if created:
                    Profile.objects.create(user=user)
            else:
                try:
                    user = User.objects.get(email=email) if email else User.objects.get(phone=phone)
                except User.DoesNotExist:
                    raise UserNotFoundError('Пользователь не найден')
            
            token = CustomTokenObtainPairSerializer.get_token(user)
            
            return self.success_response(
                data={
                    'access': str(token.access_token),
                    'refresh': str(token),
                    'role': user.role
                },
                message='Успешная верификация'
            )
            
        except BaseCustomException:
            raise
        except Exception as e:
            return self.error_response(
                error_number='VERIFICATION_ERROR',
                error_message=f'Ошибка верификации: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QuickRegisterRequestView(VerificationCodeSenderMixin, BaseAPIView):
    """
    Запросить код для быстрой регистрации.
    """
    permission_classes = [AllowAny]
    serializer_class = QuickRegisterRequestSerializer
    user_check_required = False

class QuickRegisterVerifyView(VerificationCodeVerifyMixin, BaseAPIView):
    """
    Проверить код и зарегистрировать пользователя.
    """
    permission_classes = [AllowAny]
    serializer_class = QuickRegisterVerifySerializer
    create_user_if_not_exists = True

class QuickLoginRequestView(VerificationCodeSenderMixin, BaseAPIView):
    """
    Запросить код для быстрого входа (только для существующих пользователей).
    """
    permission_classes = [AllowAny]
    serializer_class = QuickRegisterRequestSerializer
    user_check_required = True

class QuickLoginVerifyView(VerificationCodeVerifyMixin, BaseAPIView):
    """
    Проверить код и войти (только для существующих пользователей).
    """
    permission_classes = [AllowAny]
    serializer_class = QuickRegisterVerifySerializer
    create_user_if_not_exists = False

class CustomerLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Авторизация клиента (customer)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль'),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response('Успешная авторизация', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'role': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            401: 'Ошибка авторизации или роль не совпадает'
        },
        tags=['Авторизация']
    )
    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        data['role'] = 'customer'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class ProviderLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Авторизация провайдера (provider)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль'),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response('Успешная авторизация', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'role': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            401: 'Ошибка авторизации или роль не совпадает'
        },
        tags=['Авторизация']
    )
    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        data['role'] = 'provider'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class ManagementLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Авторизация менеджера (management)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль'),
            },
            required=['email', 'password'],
        ),
        responses={
            200: openapi.Response('Успешная авторизация', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                    'role': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )),
            401: 'Ошибка авторизации или роль не совпадает'
        },
        tags=['Авторизация']
    )
    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        data['role'] = 'management'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Email для подтверждения')
        }
    ),
    responses={200: 'Код отправлен', 400: 'Ошибка'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def email_confirm_request(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email обязателен'}, status=400)
    code = str(uuid.uuid4())
    EmailConfirmationCode.objects.create(email=email, code=code)
    # Реальная отправка email
    send_mail('Код подтверждения', f'Ваш код: {code}', settings.DEFAULT_FROM_EMAIL, [email])
    return Response({'success': True, 'message': 'Код подтверждения отправлен на email'}, status=200)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['email', 'code'],
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='Email для подтверждения'),
            'code': openapi.Schema(type=openapi.TYPE_STRING, description='Код подтверждения')
        }
    ),
    responses={200: 'Email подтверждён', 400: 'Ошибка'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def email_confirm_verify(request):
    email = request.data.get('email')
    code = request.data.get('code')
    if not email or not code:
        return Response({'error': 'Email и code обязательны'}, status=400)
    try:
        confirmation = EmailConfirmationCode.objects.get(email=email, code=code, is_used=False)
    except EmailConfirmationCode.DoesNotExist:
        return Response({'error': 'Неверный код или email'}, status=400)
    confirmation.is_used = True
    confirmation.save()
    # Пометить email как подтверждённый в профиле пользователя, если есть
    from .models import User, Profile
    try:
        user = User.objects.get(email=email)
        profile = Profile.objects.get(user=user)
        profile.is_email_confirmed = True
        profile.save()
    except (User.DoesNotExist, Profile.DoesNotExist):
        pass  # Если пользователя или профиля нет — просто пропускаем
    return Response({'success': True, 'message': 'Email подтверждён'}, status=200)
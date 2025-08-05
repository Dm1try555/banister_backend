from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Booking
from .serializers import (
    BookingSerializer, BookingCreateSerializer, BookingUpdateSerializer, 
    BookingStatusUpdateSerializer, ServiceSearchSerializer
)
from services.models import Service
from .google_calendar_service import google_calendar_service
from authentication.models import User

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import CustomPermissionError, ValidationError
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class BookingListView(BaseAPIView):
    """Список бронирований пользователя"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить список бронирований",
        responses={
            200: openapi.Response('Список бронирований', BookingSerializer),
            401: 'Требуется аутентификация',
            500: 'Ошибка сервера'
        },
        tags=['Bookings']
    )
    def get(self, request):
        try:
            queryset = self.get_queryset()
            serializer = BookingSerializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Список бронирований получен'
            )
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_LIST_ERROR',
                error_message=f'Ошибка получения списка: {str(e)}',
                status_code=500
            )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Booking.objects.none()
        
        if self.request.user.role == 'customer':
            return Booking.objects.filter(customer=self.request.user)
        elif self.request.user.role == 'provider':
            return Booking.objects.filter(provider=self.request.user)
        return Booking.objects.none()

class BookingCreateView(BaseAPIView):
    """Создание нового бронирования"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Создать новое бронирование (только клиенты)",
        request_body=BookingCreateSerializer,
        responses={
            201: openapi.Response('Бронирование создано', BookingSerializer),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            403: 'Только клиенты могут создавать бронирования',
            409: 'Конфликт времени',
            500: 'Ошибка сервера'
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def post(self, request):
        try:
            if request.user.role != 'customer':
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='Только клиенты могут создавать бронирования',
                    status_code=403
                )
            
            serializer = BookingCreateSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            service = serializer.validated_data.get('service')
            if not service:
                return self.error_response(
                    error_number='SERVICE_NOT_FOUND',
                    error_message='Услуга не найдена',
                    status_code=404
                )
            
            # Объединение даты и времени
            preferred_date = serializer.validated_data.get('preferred_date')
            preferred_time = serializer.validated_data.get('preferred_time')
            scheduled_datetime = datetime.combine(preferred_date, preferred_time)
            
            # Проверка конфликтов времени
            conflicting_booking = Booking.objects.filter(
                service=service,
                scheduled_datetime=scheduled_datetime,
                status__in=['confirmed', 'pending']
            ).first()
            
            if conflicting_booking:
                return self.error_response(
                    error_number='TIME_CONFLICT',
                    error_message='Выбранное время уже занято',
                    status_code=409
                )
            
            # Создание бронирования
            booking_data = serializer.validated_data.copy()
            booking_data['scheduled_datetime'] = scheduled_datetime
            booking_data['customer'] = request.user
            booking_data['provider'] = service.provider
            
            booking = Booking.objects.create(**booking_data)
            
            response_serializer = BookingSerializer(booking)
            
            return self.success_response(
                data=response_serializer.data,
                message='Бронирование создано успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_CREATE_ERROR',
                error_message=f'Ошибка создания бронирования: {str(e)}',
                status_code=500
            )

class BookingDetailView(BaseAPIView):
    """Детали бронирования"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put']  # Только GET и PUT
    
    @swagger_auto_schema(
        operation_description="Получить детали бронирования",
        responses={
            200: openapi.Response('Детали бронирования', BookingSerializer),
            401: 'Требуется аутентификация',
            404: 'Бронирование не найдено',
            500: 'Ошибка сервера'
        },
        tags=['Bookings']
    )
    def get(self, request, pk):
        try:
            instance = self.get_queryset().get(pk=pk)
            serializer = BookingSerializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Детали бронирования получены'
            )
            
        except Booking.DoesNotExist:
            return self.error_response(
                error_number='BOOKING_NOT_FOUND',
                error_message='Бронирование не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_RETRIEVE_ERROR',
                error_message=f'Ошибка получения деталей: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Обновить бронирование (только клиенты)",
        request_body=BookingUpdateSerializer,
        responses={
            200: openapi.Response('Бронирование обновлено', BookingSerializer),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            403: 'Нет прав для обновления',
            404: 'Бронирование не найдено',
            500: 'Ошибка сервера'
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def put(self, request, pk):
        try:
            instance = self.get_queryset().get(pk=pk)
            
            if request.user.role != 'customer' or instance.customer != request.user:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='Нет прав для обновления этого бронирования',
                    status_code=403
                )
            
            if instance.status in ['cancelled', 'completed']:
                return self.error_response(
                    error_number='INVALID_STATUS',
                    error_message='Нельзя изменять завершенное или отмененное бронирование',
                    status_code=400
                )
            
            serializer = BookingUpdateSerializer(instance, data=request.data, partial=False)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Обновление времени если изменились дата/время
            if 'preferred_date' in serializer.validated_data or 'preferred_time' in serializer.validated_data:
                preferred_date = serializer.validated_data.get('preferred_date', instance.preferred_date)
                preferred_time = serializer.validated_data.get('preferred_time', instance.preferred_time)
                scheduled_datetime = datetime.combine(preferred_date, preferred_time)
                serializer.validated_data['scheduled_datetime'] = scheduled_datetime
            
            booking = serializer.save()
            response_serializer = BookingSerializer(booking)
            
            return self.success_response(
                data=response_serializer.data,
                message='Бронирование обновлено успешно'
            )
            
        except Booking.DoesNotExist:
            return self.error_response(
                error_number='BOOKING_NOT_FOUND',
                error_message='Бронирование не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_UPDATE_ERROR',
                error_message=f'Ошибка обновления: {str(e)}',
                status_code=500
            )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Booking.objects.none()
        
        if self.request.user.role == 'customer':
            return Booking.objects.filter(customer=self.request.user)
        elif self.request.user.role == 'provider':
            return Booking.objects.filter(provider=self.request.user)
        return Booking.objects.none()

class BookingStatusUpdateView(BaseAPIView):
    """Обновление статуса бронирования (для провайдеров)"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Обновить статус бронирования (только провайдеры)",
        request_body=BookingStatusUpdateSerializer,
        responses={
            200: openapi.Response('Статус обновлен', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            403: 'Только провайдеры могут обновлять статус',
            404: 'Бронирование не найдено',
            500: 'Ошибка сервера'
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def post(self, request, booking_id):
        try:
            if request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='Только провайдеры могут обновлять статус',
                    status_code=403
                )
            
            try:
                booking = Booking.objects.get(id=booking_id, provider=request.user)
            except Booking.DoesNotExist:
                return self.error_response(
                    error_number='BOOKING_NOT_FOUND',
                    error_message='Бронирование не найдено',
                    status_code=404
                )
            
            serializer = BookingStatusUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            new_status = serializer.validated_data['status']
            booking.status = new_status
            booking.save()
            
            return self.success_response(
                data={'status': new_status},
                message='Статус бронирования обновлен'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='STATUS_UPDATE_ERROR',
                error_message=f'Ошибка обновления статуса: {str(e)}',
                status_code=500
            )

class ProviderSearchView(BaseAPIView):
    """Поиск доступных провайдеров"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Поиск доступных провайдеров",
        manual_parameters=[
            openapi.Parameter(
                'service_type', 
                openapi.IN_QUERY, 
                description="Тип услуги",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'location', 
                openapi.IN_QUERY, 
                description="Локация услуги",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'preferred_date', 
                openapi.IN_QUERY, 
                description="Предпочитаемая дата (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'preferred_time', 
                openapi.IN_QUERY, 
                description="Предпочитаемое время (HH:MM)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'max_price', 
                openapi.IN_QUERY, 
                description="Максимальная цена",
                type=openapi.TYPE_NUMBER,
                required=False
            ),
        ],
        responses={
            200: openapi.Response('Провайдеры найдены', ServiceSearchSerializer),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            500: 'Ошибка сервера'
        },
        tags=['Bookings']
    )
    def get(self, request):
        try:
            service_type = request.query_params.get('service_type')
            location = request.query_params.get('location')
            preferred_date_str = request.query_params.get('preferred_date')
            preferred_time_str = request.query_params.get('preferred_time')
            max_price = request.query_params.get('max_price')
            
            services = Service.objects.all()
            
            if service_type:
                services = services.filter(
                    Q(title__icontains=service_type) |
                    Q(description__icontains=service_type)
                )
            
            if max_price:
                try:
                    max_price_decimal = float(max_price)
                    services = services.filter(price__lte=max_price_decimal)
                except ValueError:
                    return self.error_response(
                        error_number='INVALID_PRICE',
                        error_message='Неверный формат цены',
                        status_code=400
                    )
            
            available_services = []
            for service in services:
                if preferred_date_str and preferred_time_str:
                    try:
                        preferred_date = datetime.strptime(preferred_date_str, '%Y-%m-%d').date()
                        preferred_time = datetime.strptime(preferred_time_str, '%H:%M').time()
                        
                        conflicting_bookings = Booking.objects.filter(
                            service=service,
                            scheduled_datetime__date=preferred_date,
                            status__in=['pending', 'confirmed']
                        )
                        
                        if not conflicting_bookings.exists():
                            available_services.append(service)
                    except ValueError:
                        return self.error_response(
                            error_number='INVALID_DATE_FORMAT',
                            error_message='Неверный формат даты или времени',
                            status_code=400
                        )
                else:
                    available_services.append(service)
            
            result_serializer = ServiceSearchSerializer(available_services, many=True)
            
            return self.success_response(
                data=result_serializer.data,
                message=f'Найдено {len(available_services)} доступных провайдеров'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PROVIDER_SEARCH_ERROR',
                error_message=f'Ошибка поиска провайдеров: {str(e)}',
                status_code=500
            )

class GoogleMeetInvitationView(BaseAPIView):
    """Тестовый эндпоинт для отправки Google Meet приглашений"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Отправить Google Meet приглашение пользователям с подтвержденной почтой",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='Список ID пользователей для отправки приглашений'
                ),
                'meeting_title': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Название встречи'
                ),
                'meeting_description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Описание встречи'
                ),
                'meeting_datetime': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format='date-time',
                    description='Дата и время встречи (ISO format)'
                ),
                'duration_minutes': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Длительность встречи в минутах (по умолчанию 60)'
                )
            },
            required=['user_ids', 'meeting_title', 'meeting_datetime']
        ),
        responses={
            200: openapi.Response('Приглашения отправлены успешно', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'calendar_created': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            'calendar_event_id': openapi.Schema(type=openapi.TYPE_STRING),
                            'emails_sent': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'total_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'confirmed_users': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING)
                            ),
                            'unconfirmed_users': openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(type=openapi.TYPE_STRING)
                            )
                        }
                    )
                }
            )),
            400: 'Ошибка валидации',
            403: 'Нет прав доступа',
            500: 'Ошибка сервера'
        },
        tags=['Google Calendar']
    )
    def post(self, request):
        """Отправить Google Meet приглашения"""
        try:
            if not request.user.is_admin_role():
                return self.error_response(
                    error_number='PERMISSION_ERROR',
                    error_message='Только администраторы могут отправлять приглашения',
                    status_code=403
                )
            
            user_ids = request.data.get('user_ids', [])
            meeting_title = request.data.get('meeting_title', '')
            meeting_description = request.data.get('meeting_description', '')
            meeting_datetime_str = request.data.get('meeting_datetime', '')
            duration_minutes = request.data.get('duration_minutes', 60)
            
            if not user_ids:
                return self.error_response(
                    error_number='VALIDATION_ERROR',
                    error_message='Список пользователей не может быть пустым',
                    status_code=400
                )
            
            if not meeting_title:
                return self.error_response(
                    error_number='VALIDATION_ERROR',
                    error_message='Название встречи обязательно',
                    status_code=400
                )
            
            if not meeting_datetime_str:
                return self.error_response(
                    error_number='VALIDATION_ERROR',
                    error_message='Дата и время встречи обязательны',
                    status_code=400
                )
            
            try:
                meeting_datetime = datetime.fromisoformat(meeting_datetime_str.replace('Z', '+00:00'))
            except ValueError:
                return self.error_response(
                    error_number='VALIDATION_ERROR',
                    error_message='Неверный формат даты и времени. Используйте ISO format',
                    status_code=400
                )
            
            users = User.objects.filter(id__in=user_ids)
            confirmed_users = []
            unconfirmed_users = []
            
            for user in users:
                if user.email and user.profile.is_email_confirmed:
                    confirmed_users.append(user)
                else:
                    unconfirmed_users.append(user)
            
            if not confirmed_users:
                return self.error_response(
                    error_number='VALIDATION_ERROR',
                    error_message='Нет пользователей с подтвержденной почтой',
                    status_code=400
                )
            
            end_datetime = meeting_datetime + timedelta(minutes=duration_minutes)
            
            class MockBooking:
                def __init__(self, title, description, start_time, end_time, users):
                    self.service = type('Service', (), {'title': title})()
                    self.scheduled_datetime = start_time
                    self.end_datetime = end_time
                    self.notes = description
                    self.customer = users[0] if users else None
                    self.provider = users[1] if len(users) > 1 else users[0]
                    self.location = 'Google Meet'
            
            mock_booking = MockBooking(
                title=meeting_title,
                description=meeting_description,
                start_time=meeting_datetime,
                end_time=end_datetime,
                users=confirmed_users
            )
            
            result = google_calendar_service.send_meeting_invitations(mock_booking)
            
            response_data = {
                'calendar_created': result['calendar_created'],
                'calendar_event_id': result['calendar_event_id'],
                'emails_sent': result['emails_sent'],
                'total_users': result['total_users'],
                'confirmed_users': [user.email for user in confirmed_users],
                'unconfirmed_users': [user.email for user in unconfirmed_users]
            }
            
            return self.success_response(
                data=response_data,
                message=f'Приглашения отправлены. Успешно: {result["emails_sent"]}/{result["total_users"]}'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='GOOGLE_MEET_ERROR',
                error_message=f'Ошибка отправки приглашений: {str(e)}',
                status_code=500
            )
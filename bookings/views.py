from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    PermissionError, NotFoundError, BookingNotFoundError,
    ValidationError, ConflictError
)
from error_handling.utils import ErrorResponseMixin, format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class BookingListCreateView(BaseAPIView, generics.ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Для генерации схемы swagger или если нет user.role — возвращаем пустой queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Booking.objects.none()
        # customer видит свои заказы, provider видит заказы на свои услуги
        if self.request.user.role == 'customer':
            return Booking.objects.filter(customer=self.request.user)
        elif self.request.user.role == 'provider':
            return Booking.objects.filter(provider=self.request.user)
        return Booking.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        # Проверка прав доступа
        if self.request.user.role != 'customer':
            raise PermissionError('Только клиенты могут создавать бронирования')
        
        # Проверка доступности времени
        service = serializer.validated_data.get('service')
        booking_date = serializer.validated_data.get('booking_date')
        booking_time = serializer.validated_data.get('booking_time')
        
        # Проверка на конфликт времени
        conflicting_booking = Booking.objects.filter(
            service=service,
            booking_date=booking_date,
            booking_time=booking_time,
            status__in=['confirmed', 'pending']
        ).first()
        
        if conflicting_booking:
            raise ConflictError('Выбранное время уже занято')
        
        booking = serializer.save(customer=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить список всех бронирований пользователя (клиент видит свои, провайдер — свои)",
        responses={
            200: openapi.Response('Список бронирований', BookingSerializer(many=True)),
            403: 'Нет прав доступа',
        },
        tags=['Бронирования']
    )
    def list(self, request, *args, **kwargs):
        """
        Получение списка бронирований
        """
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Список бронирований получен успешно'
            )
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_LIST_ERROR',
                error_message=f'Ошибка получения списка бронирований: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Создать новое бронирование (только для клиентов)",
        request_body=BookingSerializer,
        responses={
            201: openapi.Response('Бронирование создано', BookingSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав доступа',
            409: 'Конфликт времени',
        },
        tags=['Бронирования']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Создание нового бронирования
        """
        try:
            # Проверка прав доступа
            if self.request.user.role != 'customer':
                raise PermissionError('Только клиенты могут создавать бронирования')
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Проверка доступности времени
            service = serializer.validated_data.get('service')
            booking_date = serializer.validated_data.get('booking_date')
            booking_time = serializer.validated_data.get('booking_time')
            
            # Проверка на конфликт времени
            conflicting_booking = Booking.objects.filter(
                service=service,
                booking_date=booking_date,
                booking_time=booking_time,
                status__in=['confirmed', 'pending']
            ).first()
            
            if conflicting_booking:
                raise ConflictError('Выбранное время уже занято')
            
            booking = serializer.save(customer=self.request.user)
            
            return self.success_response(
                data=serializer.data,
                message='Бронирование создано успешно'
            )
            
        except PermissionError:
            raise
        except ConflictError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_CREATE_ERROR',
                error_message=f'Ошибка создания бронирования: {str(e)}',
                status_code=500
            )

class BookingDetailView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Для генерации схемы swagger или если нет user.role — возвращаем пустой queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Booking.objects.none()
        # customer видит свои заказы, provider видит заказы на свои услуги
        if self.request.user.role == 'customer':
            return Booking.objects.filter(customer=self.request.user)
        elif self.request.user.role == 'provider':
            return Booking.objects.filter(provider=self.request.user)
        return Booking.objects.none()

    @swagger_auto_schema(
        operation_description="Получить подробную информацию о бронировании по ID (только для владельца)",
        responses={
            200: openapi.Response('Информация о бронировании', BookingSerializer),
            404: 'Бронирование не найдено',
        },
        tags=['Бронирования']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Получение детальной информации о бронировании
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Информация о бронировании получена успешно'
            )
            
        except Booking.DoesNotExist:
            raise BookingNotFoundError('Бронирование не найдено')
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_RETRIEVE_ERROR',
                error_message=f'Ошибка получения информации о бронировании: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Обновить данные бронирования (только для владельца)",
        request_body=BookingSerializer,
        responses={
            200: openapi.Response('Бронирование обновлено', BookingSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
            404: 'Бронирование не найдено',
        },
        tags=['Бронирования']
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Обновление бронирования
        """
        try:
            instance = self.get_object()
            
            # Проверка прав на обновление
            if self.request.user.role == 'customer' and instance.customer != self.request.user:
                raise PermissionError('Нет прав для обновления этого бронирования')
            
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Проверка статуса бронирования
            if instance.status in ['cancelled', 'completed']:
                raise ValidationError('Нельзя изменить завершенное или отмененное бронирование')
            
            booking = serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message='Бронирование обновлено успешно'
            )
            
        except Booking.DoesNotExist:
            raise BookingNotFoundError('Бронирование не найдено')
        except PermissionError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_UPDATE_ERROR',
                error_message=f'Ошибка обновления бронирования: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Удалить бронирование (только для владельца)",
        responses={
            200: 'Бронирование удалено',
            403: 'Нет прав',
            404: 'Бронирование не найдено',
        },
        tags=['Бронирования']
    )
    def destroy(self, request, *args, **kwargs):
        """
        Удаление бронирования
        """
        try:
            instance = self.get_object()
            
            # Проверка прав на удаление
            if self.request.user.role == 'customer' and instance.customer != self.request.user:
                raise PermissionError('Нет прав для удаления этого бронирования')
            
            # Проверка возможности отмены
            if instance.status in ['completed', 'cancelled']:
                raise ValidationError('Нельзя удалить завершенное или отмененное бронирование')
            
            instance.delete()
            
            return self.success_response(
                message='Бронирование удалено успешно'
            )
            
        except Booking.DoesNotExist:
            raise BookingNotFoundError('Бронирование не найдено')
        except PermissionError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_DELETE_ERROR',
                error_message=f'Ошибка удаления бронирования: {str(e)}',
                status_code=500
            )

class BookingStatusUpdateView(BaseAPIView):
    """
    Обновление статуса бронирования (для провайдеров)
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Изменить статус бронирования (только для провайдера)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Новый статус'),
            },
            required=['status'],
        ),
        responses={
            200: 'Статус обновлен',
            400: 'Ошибка запроса',
            403: 'Нет прав',
            404: 'Бронирование не найдено',
        },
        tags=['Бронирования']
    )
    def post(self, request, booking_id):
        try:
            # Проверка роли пользователя
            if self.request.user.role != 'provider':
                raise PermissionError('Только поставщики услуг могут изменять статус бронирования')
            
            # Получение бронирования
            try:
                booking = Booking.objects.get(id=booking_id, provider=self.request.user)
            except Booking.DoesNotExist:
                raise BookingNotFoundError('Бронирование не найдено')
            
            new_status = request.data.get('status')
            if not new_status:
                return self.error_response(
                    error_number='MISSING_STATUS',
                    error_message='Статус не указан',
                    status_code=400
                )
            
            # Проверка валидности статуса
            valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
            if new_status not in valid_statuses:
                return self.error_response(
                    error_number='INVALID_STATUS',
                    error_message=f'Неверный статус. Допустимые значения: {", ".join(valid_statuses)}',
                    status_code=400
                )
            
            # Обновление статуса
            booking.status = new_status
            booking.save()
            
            return self.success_response(
                data={'status': new_status},
                message='Статус бронирования обновлен успешно'
            )
            
        except PermissionError:
            raise
        except BookingNotFoundError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='STATUS_UPDATE_ERROR',
                error_message=f'Ошибка обновления статуса: {str(e)}',
                status_code=500
            )
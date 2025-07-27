from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Schedule
from .serializers import ScheduleSerializer

# Импорт системы обработки ошибок
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    PermissionError, ValidationError, NotFoundError, ConflictError
)
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class ScheduleListCreateView(BaseAPIView, generics.ListCreateAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Для генерации схемы swagger или если нет user.role — возвращаем пустой queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Schedule.objects.none()
        return Schedule.objects.filter(provider=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        # Проверка роли пользователя
        if self.request.user.role != 'provider':
            raise PermissionError('Только поставщики услуг могут создавать расписание')
        
        # Проверка на конфликт времени
        start_time = serializer.validated_data.get('start_time')
        end_time = serializer.validated_data.get('end_time')
        date = serializer.validated_data.get('date')
        
        conflicting_schedule = Schedule.objects.filter(
            provider=self.request.user,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).first()
        
        if conflicting_schedule:
            raise ConflictError('Выбранное время уже занято в расписании')
        
        serializer.save(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить расписание провайдера (все слоты)",
        responses={
            200: openapi.Response('Список расписаний', ScheduleSerializer(many=True)),
        },
        tags=['Расписание']
    )
    def list(self, request, *args, **kwargs):
        try:
            # Фильтрация расписания по провайдеру
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Расписание получено успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_LIST_ERROR',
                error_message=f'Ошибка получения расписания: {str(e)}',
                status_code=500
            )

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="Создать новый слот в расписании (только для провайдера)",
        request_body=ScheduleSerializer,
        responses={
            201: openapi.Response('Расписание создано', ScheduleSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
            409: 'Конфликт времени',
        },
        tags=['Расписание']
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Расписание создано успешно'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_CREATE_ERROR',
                error_message=f'Ошибка создания расписания: {str(e)}',
                status_code=500
            )

class ScheduleDetailView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Для генерации схемы swagger или если нет user.role — возвращаем пустой queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Schedule.objects.none()
        return Schedule.objects.filter(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить подробную информацию о слоте расписания по ID",
        responses={
            200: openapi.Response('Информация о расписании', ScheduleSerializer),
            404: 'Расписание не найдено',
        },
        tags=['Расписание']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Проверка прав доступа
            if instance.provider != self.request.user:
                raise PermissionError('Нет прав для просмотра этого расписания')
            
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Информация о расписании получена успешно'
            )
            
        except Schedule.DoesNotExist:
            return self.error_response(
                error_number='SCHEDULE_NOT_FOUND',
                error_message='Расписание не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_RETRIEVE_ERROR',
                error_message=f'Ошибка получения информации о расписании: {str(e)}',
                status_code=500
            )

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="Обновить слот расписания (только для владельца)",
        request_body=ScheduleSerializer,
        responses={
            200: openapi.Response('Расписание обновлено', ScheduleSerializer),
            400: 'Ошибка валидации',
            403: 'Нет прав',
            404: 'Расписание не найдено',
            409: 'Конфликт времени',
        },
        tags=['Расписание']
    )
    def update(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_update(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Расписание обновлено успешно'
            )
            
        except Schedule.DoesNotExist:
            return self.error_response(
                error_number='SCHEDULE_NOT_FOUND',
                error_message='Расписание не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_UPDATE_ERROR',
                error_message=f'Ошибка обновления расписания: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Удалить слот расписания (только для владельца)",
        responses={
            200: 'Расписание удалено',
            403: 'Нет прав',
            404: 'Расписание не найдено',
        },
        tags=['Расписание']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            self.perform_destroy(self.get_object())
            
            return self.success_response(
                message='Расписание удалено успешно'
            )
            
        except Schedule.DoesNotExist:
            return self.error_response(
                error_number='SCHEDULE_NOT_FOUND',
                error_message='Расписание не найдено',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_DELETE_ERROR',
                error_message=f'Ошибка удаления расписания: {str(e)}',
                status_code=500
            )
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Schedule
from .serializers import ScheduleSerializer
from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class ScheduleListView(BaseAPIView):
    """Список расписания провайдера"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Получить расписание провайдера",
        responses={200: openapi.Response('Список расписания', ScheduleSerializer(many=True))},
        tags=['Schedule']
    )
    def get(self, request):
        """Получить список расписания"""
        try:
            if getattr(self, 'swagger_fake_view', False) or not hasattr(request.user, 'role'):
                return self.success_response(data=[], message='Расписание получено')
            
            schedules = Schedule.objects.filter(provider=request.user)
            serializer = ScheduleSerializer(schedules, many=True)
            
            return self.success_response(
                data=serializer.data, 
                message='Расписание получено'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_LIST_ERROR',
                error_message=f'Ошибка получения расписания: {str(e)}',
                status_code=500
            )

class ScheduleCreateView(BaseAPIView):
    """Создание нового слота расписания"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']  # Только POST
    
    @swagger_auto_schema(
        operation_description="Создать новый слот расписания (только провайдеры)",
        request_body=ScheduleSerializer,
        responses={201: openapi.Response('Расписание создано', ScheduleSerializer)},
        tags=['Schedule']
    )
    @transaction.atomic
    def post(self, request):
        """Создать новый слот расписания"""
        try:
            if request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='Только провайдеры могут создавать расписание',
                    status_code=403
                )
            
            serializer = ScheduleSerializer(data=request.data)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            start_time = serializer.validated_data.get('start_time')
            end_time = serializer.validated_data.get('end_time')
            date = serializer.validated_data.get('date')
            
            # Проверка конфликтов времени
            conflicting_schedule = Schedule.objects.filter(
                provider=request.user,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time
            ).first()
            
            if conflicting_schedule:
                return self.error_response(
                    error_number='TIME_CONFLICT',
                    error_message='Выбранное время уже занято',
                    status_code=409
                )
            
            schedule = serializer.save(provider=request.user)
            
            return self.success_response(
                data=ScheduleSerializer(schedule).data, 
                message='Расписание создано'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_CREATE_ERROR',
                error_message=f'Ошибка создания расписания: {str(e)}',
                status_code=500
            )

class ScheduleDetailView(BaseAPIView):
    """Детали расписания"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'delete']  # GET, PUT, DELETE
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Schedule.objects.none()
        return Schedule.objects.filter(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить информацию о слоте расписания",
        responses={200: openapi.Response('Информация о расписании', ScheduleSerializer)},
        tags=['Schedule']
    )
    def get(self, request, pk):
        """Получить детали расписания"""
        try:
            schedule = self.get_queryset().get(pk=pk)
            serializer = ScheduleSerializer(schedule)
            
            return self.success_response(
                data=serializer.data, 
                message='Информация о расписании получена'
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
                error_message=f'Ошибка получения расписания: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Обновить слот расписания (только владелец)",
        request_body=ScheduleSerializer,
        responses={200: openapi.Response('Расписание обновлено', ScheduleSerializer)},
        tags=['Schedule']
    )
    @transaction.atomic
    def put(self, request, pk):
        """Обновить расписание"""
        try:
            schedule = self.get_queryset().get(pk=pk)
            
            serializer = ScheduleSerializer(schedule, data=request.data, partial=False)
            if not serializer.is_valid():
                # Позволяем Django обработать стандартные ошибки валидации
                serializer.is_valid(raise_exception=True)
            
            updated_schedule = serializer.save()
            
            return self.success_response(
                data=ScheduleSerializer(updated_schedule).data, 
                message='Расписание обновлено'
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
        operation_description="Удалить слот расписания (только владелец)",
        responses={200: 'Расписание удалено'},
        tags=['Schedule']
    )
    @transaction.atomic
    def delete(self, request, pk):
        """Удалить расписание"""
        try:
            schedule = self.get_queryset().get(pk=pk)
            schedule.delete()
            
            return self.success_response(
                message='Расписание удалено'
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
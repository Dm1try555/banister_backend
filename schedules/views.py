from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Schedule
from .serializers import ScheduleSerializer
from error_handling.views import BaseAPIView
from error_handling.exceptions import CustomPermissionError, ConflictError
from error_handling.utils import format_validation_errors
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class ScheduleListCreateView(BaseAPIView, generics.ListCreateAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Schedule.objects.none()
        return Schedule.objects.filter(provider=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        if self.request.user.role != 'provider':
            raise CustomPermissionError('Только провайдеры могут создавать расписание')
        
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
            raise ConflictError('Выбранное время уже занято')
        
        serializer.save(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить расписание провайдера",
        responses={200: openapi.Response('Список расписания', ScheduleSerializer(many=True))},
        tags=['Schedule']
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.success_response(data=serializer.data, message='Расписание получено')

    @swagger_auto_schema(
        operation_description="Создать новый слот расписания (только провайдеры)",
        request_body=ScheduleSerializer,
        responses={201: openapi.Response('Расписание создано', ScheduleSerializer)},
        tags=['Schedule']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            field_errors = format_validation_errors(serializer.errors)
            return self.validation_error_response(field_errors)
        
        self.perform_create(serializer)
        return self.success_response(data=serializer.data, message='Расписание создано')

class ScheduleDetailView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Schedule.objects.none()
        return Schedule.objects.filter(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Получить информацию о слоте расписания",
        responses={200: openapi.Response('Информация о расписании', ScheduleSerializer)},
        tags=['Schedule']
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.provider != self.request.user:
            raise CustomPermissionError('Нет прав для просмотра этого расписания')
        
        serializer = self.get_serializer(instance)
        return self.success_response(data=serializer.data, message='Информация о расписании получена')

    @swagger_auto_schema(
        operation_description="Обновить слот расписания (только владелец)",
        request_body=ScheduleSerializer,
        responses={200: openapi.Response('Расписание обновлено', ScheduleSerializer)},
        tags=['Schedule']
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        if not serializer.is_valid():
            field_errors = format_validation_errors(serializer.errors)
            return self.validation_error_response(field_errors)
        
        self.perform_update(serializer)
        return self.success_response(data=serializer.data, message='Расписание обновлено')

    @swagger_auto_schema(
        operation_description="Удалить слот расписания (только владелец)",
        responses={200: 'Расписание удалено'},
        tags=['Schedule']
    )
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())
        return self.success_response(message='Расписание удалено')
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.utils import timezone
from .models import DataProcessingTask
from .serializers import (
    DataProcessingTaskSerializer, CreateTaskSerializer, 
    TaskStatusSerializer
)
from .worker import (
    DataProcessingWorker, BookingDataWorker, PaymentDataWorker,
    UserDataWorker, ServiceDataWorker
)
from error_handling.views import BaseAPIView
from error_handling.utils import format_validation_errors
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import threading

class WorkerPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class WorkersViewSet(BaseAPIView):
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]
    pagination_class = WorkerPagination

    @swagger_auto_schema(
        operation_description="Получить список задач обработки данных",
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY, description="Фильтр по статусу задачи",
                type=openapi.TYPE_STRING, enum=['pending', 'processing', 'completed', 'failed', 'cancelled'], required=False),
            openapi.Parameter(
                'task_type', openapi.IN_QUERY, description="Фильтр по типу задачи",
                type=openapi.TYPE_STRING, required=False),
        ],
        responses={200: openapi.Response('Список задач', DataProcessingTaskSerializer(many=True))},
        tags=['Workers']
    )
    def get(self, request):
        queryset = self._get_filtered_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DataProcessingTaskSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = DataProcessingTaskSerializer(queryset, many=True)
        return self.success_response(data=serializer.data, message='Список задач получен успешно')

    @swagger_auto_schema(
        operation_description="Создать новую задачу обработки данных",
        request_body=CreateTaskSerializer,
        responses={201: openapi.Response('Задача создана', DataProcessingTaskSerializer)},
        tags=['Workers']
    )
    @transaction.atomic
    def post(self, request):
        serializer = CreateTaskSerializer(data=request.data)
        if not serializer.is_valid():
            field_errors = format_validation_errors(serializer.errors)
            return self.validation_error_response(field_errors)
        task = serializer.save(created_by=request.user)
        self._start_processing_async(task.id)
        response_serializer = DataProcessingTaskSerializer(task)
        return self.success_response(data=response_serializer.data, message='Задача создана и запущена в обработку', status_code=201)

    def _get_filtered_queryset(self):
        queryset = DataProcessingTask.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        task_type = self.request.query_params.get('task_type')
        if task_type:
            queryset = queryset.filter(task_type=task_type)
        if not self.request.user.is_staff:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset.order_by('-created_at')

    def _start_processing_async(self, task_id):
        def process_task():
            try:
                task = DataProcessingTask.objects.get(id=task_id)
                if task.task_type == 'bookings_export':
                    worker = BookingDataWorker(task_id)
                elif task.task_type == 'payments_export':
                    worker = PaymentDataWorker(task_id)
                elif task.task_type == 'users_export':
                    worker = UserDataWorker(task_id)
                elif task.task_type == 'services_export':
                    worker = ServiceDataWorker(task_id)
                else:
                    worker = DataProcessingWorker(task_id)
                worker.process_task()
            except Exception as e:
                print(f"Ошибка обработки задачи {task_id}: {str(e)}")
        thread = threading.Thread(target=process_task)
        thread.daemon = True
        thread.start()

class WorkerDetailView(BaseAPIView):
    http_method_names = ['get', 'delete']
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получить детальную информацию о задаче",
        responses={200: openapi.Response('Детали задачи', DataProcessingTaskSerializer)},
        tags=['Workers']
    )
    def get(self, request, task_id):
        task = self._get_task_with_permissions(request, task_id)
        serializer = DataProcessingTaskSerializer(task)
        return self.success_response(data=serializer.data, message='Детали задачи получены успешно')

    @swagger_auto_schema(
        operation_description="Отменить задачу обработки",
        responses={200: openapi.Response('Задача отменена', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)}))},
        tags=['Workers']
    )
    @transaction.atomic
    def delete(self, request, task_id):
        task = self._get_task_with_permissions(request, task_id)
        if task.status in ['completed', 'failed', 'cancelled']:
            return self.error_response(error_number='TASK_CANNOT_CANCEL', error_message='Задача не может быть отменена', status_code=400)
        task.status = 'cancelled'
        task.completed_at = timezone.now()
        task.save()
        return self.success_response(data={'status': 'cancelled'}, message='Задача отменена успешно')

    def _get_task_with_permissions(self, request, task_id):
        if not request.user.is_staff:
            return DataProcessingTask.objects.get(id=task_id, created_by=request.user)
        else:
            return DataProcessingTask.objects.get(id=task_id)

class WorkerStatusView(BaseAPIView):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Получить статус задачи обработки",
        responses={200: openapi.Response('Статус задачи', TaskStatusSerializer)},
        tags=['Workers']
    )
    def get(self, request, task_id):
        if not request.user.is_staff:
            task = DataProcessingTask.objects.get(id=task_id, created_by=request.user)
        else:
            task = DataProcessingTask.objects.get(id=task_id)
        serializer = TaskStatusSerializer(task)
        return self.success_response(data=serializer.data, message='Статус задачи получен успешно') 
from core.base.common_imports import *
from .models import Service, Schedule
from .serializers import (
    ServiceSerializer, ServiceCreateSerializer, ServiceUpdateSerializer,
    ScheduleSerializer, ScheduleCreateSerializer, ScheduleUpdateSerializer
)
from .permissions import ServicePermissions, SchedulePermissions


class ServiceListCreateView(OptimizedListCreateView, ServicePermissions):
    permission_classes = [AllowAny]  # All can view, but only authorized can create
    queryset = Service.objects.select_related('provider').order_by('-created_at')
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'price', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        return ServiceCreateSerializer if self.request.method == 'POST' else ServiceSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        # Check permission to create
        self.check_permission('create_service')
        serializer.save(provider=self.request.user)


class ServiceDetailView(OptimizedRetrieveUpdateDestroyView, ServicePermissions):
    permission_classes = [AllowAny]  # All can view
    queryset = Service.objects.select_related('provider').order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ServiceUpdateSerializer
        return ServiceSerializer



    @transaction.atomic
    def put(self, request, *args, **kwargs):
        self.check_permission('edit_service')
        return super().put(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        self.check_permission('edit_service')
        return super().patch(request, *args, **kwargs)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        self.check_permission('delete_service')
        return super().delete(request, *args, **kwargs)


class ScheduleListCreateView(OptimizedListCreateView, SchedulePermissions):
    permission_classes = [AllowAny]  # All can view
    queryset = Schedule.objects.select_related('provider', 'service', 'service__provider').order_by('-created_at')

    def get_serializer_class(self):
        return ScheduleCreateSerializer if self.request.method == 'POST' else ScheduleSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        # Check permission to create
        self.check_permission('create_schedule')
        serializer.save(provider=self.request.user)


class ScheduleDetailView(OptimizedRetrieveUpdateDestroyView, SchedulePermissions):
    permission_classes = [AllowAny]  # All can view
    queryset = Schedule.objects.select_related('provider', 'service', 'service__provider').order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ScheduleUpdateSerializer
        return ScheduleSerializer



    @transaction.atomic
    def put(self, request, *args, **kwargs):
        self.check_permission('edit_schedule')
        return super().put(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        self.check_permission('edit_schedule')
        return super().patch(request, *args, **kwargs)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        self.check_permission('delete_schedule')
        return super().delete(request, *args, **kwargs)

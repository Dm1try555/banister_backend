from core.base.common_imports import *
from .models import Service, Schedule
from .serializers import (
    ServiceSerializer, ServiceCreateSerializer, ServiceUpdateSerializer,
    ScheduleSerializer, ScheduleCreateSerializer, ScheduleUpdateSerializer
)
from .permissions import ServicePermissions, SchedulePermissions


class ServiceListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, ServicePermissions):
    permission_classes = [AllowAny]  # All can view, but only authorized can create
    queryset = Service.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['title', 'price', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        return ServiceCreateSerializer if self.request.method == 'POST' else ServiceSerializer

    def perform_create(self, serializer):
        # Check permission to create
        self.check_permission('create_service')
        serializer.save(provider=self.request.user)


class ServiceDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin, ServicePermissions):
    permission_classes = [AllowAny]  # All can view
    queryset = Service.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ServiceUpdateSerializer
        return ServiceSerializer



    def put(self, request, *args, **kwargs):
        self.check_permission('edit_service')
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.check_permission('edit_service')
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.check_permission('delete_service')
        return super().delete(request, *args, **kwargs)


class ScheduleListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, SchedulePermissions):
    permission_classes = [AllowAny]  # All can view
    queryset = Schedule.objects.all()

    def get_serializer_class(self):
        return ScheduleCreateSerializer if self.request.method == 'POST' else ScheduleSerializer

    def perform_create(self, serializer):
        # Check permission to create
        self.check_permission('create_schedule')
        serializer.save(provider=self.request.user)


class ScheduleDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin, SchedulePermissions):
    permission_classes = [AllowAny]  # All can view
    queryset = Schedule.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ScheduleUpdateSerializer
        return ScheduleSerializer



    def put(self, request, *args, **kwargs):
        self.check_permission('edit_schedule')
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.check_permission('edit_schedule')
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.check_permission('delete_schedule')
        return super().delete(request, *args, **kwargs)

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

    @swagger_retrieve_update_destroy(
        description="Retrieve, update or delete service",
        response_schema=SERVICE_RESPONSE_SCHEMA,
        tags=["Services"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.check_permission('edit_service')
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.check_permission('edit_service')
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete service",
        response_schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        tags=["Services"]
    )
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

    @swagger_retrieve_update_destroy(
        description="Retrieve, update or delete schedule",
        response_schema=SCHEDULE_RESPONSE_SCHEMA,
        tags=["Schedules"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.check_permission('edit_schedule')
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.check_permission('edit_schedule')
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete schedule",
        response_schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        tags=["Schedules"]
    )
    def delete(self, request, *args, **kwargs):
        self.check_permission('delete_schedule')
        return super().delete(request, *args, **kwargs)

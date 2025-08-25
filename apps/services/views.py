from core.base.common_imports import *
from core.base.role_base import RoleBase
from .models import Service, Schedule
from .serializers import (
    ServiceSerializer, ServiceCreateSerializer, ServiceUpdateSerializer,
    ScheduleSerializer, ScheduleCreateSerializer, ScheduleUpdateSerializer
)


class ServiceListCreateView(SwaggerMixin, ListCreateAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Service.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Service, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Service, user)
        return self._get_admin_queryset(Service, user)

    def get_serializer_class(self):
        return ServiceCreateSerializer if self.request.method == 'POST' else ServiceSerializer

    @swagger_list_create(
        description="Create new service",
        response_schema=SERVICE_RESPONSE_SCHEMA,
        tags=["Services"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class ServiceDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Service.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Service, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Service, user)
        return self._get_admin_queryset(Service, user)

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

    @swagger_retrieve_update_destroy(
        description="Update service",
        response_schema=SERVICE_RESPONSE_SCHEMA,
        tags=["Services"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Partially update service",
        response_schema=SERVICE_RESPONSE_SCHEMA,
        tags=["Services"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete service",
        response_schema=openapi.Response(description="Service deleted successfully"),
        tags=["Services"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ScheduleListCreateView(SwaggerMixin, ListCreateAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Schedule.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Schedule, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Schedule, user)
        return self._get_admin_queryset(Schedule, user)

    def get_serializer_class(self):
        return ScheduleCreateSerializer if self.request.method == 'POST' else ScheduleSerializer

    @swagger_list_create(
        description="Create new schedule",
        response_schema=SCHEDULE_RESPONSE_SCHEMA,
        tags=["Schedules"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)


class ScheduleDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Schedule.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Schedule, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Schedule, user)
        return self._get_admin_queryset(Schedule, user)

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

    @swagger_retrieve_update_destroy(
        description="Update schedule",
        response_schema=SCHEDULE_RESPONSE_SCHEMA,
        tags=["Schedules"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Partially update schedule",
        response_schema=SCHEDULE_RESPONSE_SCHEMA,
        tags=["Schedules"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete schedule",
        response_schema=openapi.Response(description="Schedule deleted successfully"),
        tags=["Schedules"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

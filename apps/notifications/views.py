from core.base.common_imports import *
from core.base.role_base import RoleBase
from .models import Notification
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer, NotificationUpdateSerializer
)


class NotificationListCreateView(SwaggerMixin, ListCreateAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Notification, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Notification, user)
        return self._get_admin_queryset(Notification, user)

    def get_serializer_class(self):
        return NotificationCreateSerializer if self.request.method == 'POST' else NotificationSerializer

    @swagger_list_create(
        description="Create new notification",
        response_schema=NOTIFICATION_RESPONSE_SCHEMA,
        tags=["Notifications"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Notification.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Notification, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Notification, user)
        return self._get_admin_queryset(Notification, user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NotificationUpdateSerializer
        return NotificationSerializer

    @swagger_retrieve_update_destroy(
        description="Retrieve, update or delete notification",
        response_schema=NOTIFICATION_RESPONSE_SCHEMA,
        tags=["Notifications"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Update notification",
        response_schema=NOTIFICATION_RESPONSE_SCHEMA,
        tags=["Notifications"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Partially update notification",
        response_schema=NOTIFICATION_RESPONSE_SCHEMA,
        tags=["Notifications"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete notification",
        response_schema=openapi.Response(description="Notification deleted successfully"),
        tags=["Notifications"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
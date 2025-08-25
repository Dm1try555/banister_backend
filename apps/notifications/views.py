from core.base.common_imports import *
from .models import Notification
from .serializers import (
    NotificationSerializer, NotificationCreateSerializer, NotificationUpdateSerializer
)
from .permissions import NotificationPermissions


class NotificationListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, NotificationPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

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


class NotificationDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin, NotificationPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()

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
        response_schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        tags=["Notifications"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
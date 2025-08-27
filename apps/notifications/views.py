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


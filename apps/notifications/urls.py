from django.urls import path
from .views import (
    NotificationListCreateView, NotificationDetailView,
    NotificationMarkAsReadView, NotificationDeleteAllView,
    NotificationMarkAllAsReadView, NotificationUnreadCountView
)

urlpatterns = [
    # Notification URLs
    path('notifications/', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:pk>/mark-read/', NotificationMarkAsReadView.as_view(), name='notification-mark-read'),
    path('notifications/delete-all/', NotificationDeleteAllView.as_view(), name='notification-delete-all'),
    path('notifications/mark-all-read/', NotificationMarkAllAsReadView.as_view(), name='notification-mark-all-read'),
    path('notifications/unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
]
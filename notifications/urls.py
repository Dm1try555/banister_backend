from django.urls import path
from .views import (
    NotificationListView, NotificationDetailView, NotificationMarkAsReadView,
    NotificationMarkAllAsReadView, NotificationDeleteAllView, NotificationCreateView
)

app_name = 'notifications'

urlpatterns = [
    # Основной API для уведомлений
    path('', NotificationListView.as_view(), name='notification-list'),
    
    # Создание уведомления (внутренний API)
    path('create/', NotificationCreateView.as_view(), name='notification-create'),
    
    # Работа с конкретным уведомлением
    path('<int:notification_id>/', NotificationDetailView.as_view(), name='notification-detail'),
    
    # Отметить уведомление как прочитанное
    path('<int:notification_id>/read/', NotificationMarkAsReadView.as_view(), name='notification-mark-read'),
    
    # Массовые операции
    path('mark-all-read/', NotificationMarkAllAsReadView.as_view(), name='notification-mark-all-read'),
    path('delete-all/', NotificationDeleteAllView.as_view(), name='notification-delete-all'),
] 
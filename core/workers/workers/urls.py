from django.urls import path
from .views import (
    WorkersViewSet, WorkerDetailView, WorkerStatusView
)

app_name = 'workers'

urlpatterns = [
    # Основной API для управления задачами
    path('', WorkersViewSet.as_view(), name='workers'),
    
    # Детали и управление конкретной задачей
    path('<int:task_id>/', WorkerDetailView.as_view(), name='worker-detail'),
    
    # Статус задачи
    path('<int:task_id>/status/', WorkerStatusView.as_view(), name='worker-status'),
] 
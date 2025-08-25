from django.urls import path
from .views import (
    ServiceListCreateView, ServiceDetailView,
    ScheduleListCreateView, ScheduleDetailView
)

urlpatterns = [
    # Service URLs
    path('services/', ServiceListCreateView.as_view(), name='service-list-create'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
    
    # Schedule URLs
    path('schedules/', ScheduleListCreateView.as_view(), name='schedule-list-create'),
    path('schedules/<int:pk>/', ScheduleDetailView.as_view(), name='schedule-detail'),
]
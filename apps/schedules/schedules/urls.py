from django.urls import path
from .views import ScheduleListView, ScheduleCreateView, ScheduleDetailView

urlpatterns = [
    path('', ScheduleListView.as_view(), name='schedule-list'),
    path('create/', ScheduleCreateView.as_view(), name='schedule-create'),
    path('<int:pk>', ScheduleDetailView.as_view(), name='schedule-detail'),
]
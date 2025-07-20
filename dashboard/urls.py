from django.urls import path
from .views import DashboardOverviewView, DashboardStatisticsView

urlpatterns = [
    path('overview', DashboardOverviewView.as_view(), name='dashboard-overview'),
    path('statistics', DashboardStatisticsView.as_view(), name='dashboard-statistics'),
]
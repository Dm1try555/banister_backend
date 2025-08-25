from django.urls import path
from .views import (
    CustomerDashboardView, ProviderDashboardView, ManagementDashboardView
)

urlpatterns = [
    # Dashboard URLs
    path('customer-dashboard/', CustomerDashboardView.as_view(), name='customer-dashboard'),
    path('provider-dashboard/', ProviderDashboardView.as_view(), name='provider-dashboard'),
    path('management-dashboard/', ManagementDashboardView.as_view(), name='management-dashboard'),
]
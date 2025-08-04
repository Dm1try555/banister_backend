from django.urls import path
from .views import (
    AdminUserListView, AdminUserDetailView,
    CustomerListView, ProviderListView
)

urlpatterns = [
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('management/customers/', CustomerListView.as_view(), name='management-customers'),
    path('management/providers/', ProviderListView.as_view(), name='management-providers'),
]
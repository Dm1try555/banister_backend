from django.urls import path
from .views import (
    AdminUserListView, AdminUserDetailView,
    AdminIssueListCreateView, AdminIssueDetailView,
    CustomerListView, ProviderListView
)

urlpatterns = [
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('issues/', AdminIssueListCreateView.as_view(), name='admin-issue-list-create'),
    path('issues/<int:pk>/', AdminIssueDetailView.as_view(), name='admin-issue-detail'),
    path('management/customers/', CustomerListView.as_view(), name='management-customers'),
    path('management/providers/', ProviderListView.as_view(), name='management-providers'),
]
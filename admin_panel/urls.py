from django.urls import path
from .views import AdminUserListView, AdminUserDetailView, AdminIssueListView, AdminIssueResolveView

urlpatterns = [
    path('users', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('issues', AdminIssueListView.as_view(), name='admin-issue-list'),
    path('issues/resolve/<int:pk>', AdminIssueResolveView.as_view(), name='admin-issue-resolve'),
]
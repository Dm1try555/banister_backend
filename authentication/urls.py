# authentication/urls.py
from django.urls import path
from .views import (
    CustomerRegistrationView, ProviderRegistrationView, ManagementRegistrationView,
    CustomTokenObtainPairView, ProfileView,
    password_reset_request, password_reset_confirm, logout_view,
    CustomerLoginView, ProviderLoginView, ManagementLoginView,
    AdminLoginView, SuperAdminLoginView, AccountantLoginView,
    CustomTokenRefreshView, email_confirm_request, email_confirm_verify,
    AdminProfileUpdateView, AdminPermissionGrantView, AdminPermissionRevokeView, AdminPermissionListView, AdminPermissionDeleteView, AdminPermissionDetailView,

    CreateAdminView, CreateAccountantView, CreateSupportManagerView,
    AccountantCRUDView, SupportManagerCRUDView
)

urlpatterns = [
    path('register/customer/', CustomerRegistrationView.as_view(), name='register-customer'),
    path('register/provider/', ProviderRegistrationView.as_view(), name='register-provider'),
    path('register/management/', ManagementRegistrationView.as_view(), name='register-management'),
    path('login/customer/', CustomerLoginView.as_view(), name='login-customer'),
    path('login/provider/', ProviderLoginView.as_view(), name='login-provider'),
    path('login/management/', ManagementLoginView.as_view(), name='login-management'),
    path('login/admin/', AdminLoginView.as_view(), name='login-admin'),
    path('login/superadmin/', SuperAdminLoginView.as_view(), name='login-superadmin'),
    path('login/accountant/', AccountantLoginView.as_view(), name='login-accountant'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-reset/request/', password_reset_request, name='password-reset-request'),
    path('password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
    path('email-confirm/request/', email_confirm_request, name='email_confirm_request'),
    path('email-confirm/verify/', email_confirm_verify, name='email_confirm_verify'),
    
    # Admin Management URLs
    path('admin/profile/update/', AdminProfileUpdateView.as_view(), name='admin-profile-update'),
    path('admin/permissions/grant/', AdminPermissionGrantView.as_view(), name='admin-permissions-grant'),
    path('admin/permissions/revoke/', AdminPermissionRevokeView.as_view(), name='admin-permissions-revoke'),
    path('admin/permissions/list/', AdminPermissionListView.as_view(), name='admin-permissions-list'),
    path('admin/permissions/delete/', AdminPermissionDeleteView.as_view(), name='admin-permissions-delete'),
    path('admin/permissions/detail/', AdminPermissionDetailView.as_view(), name='admin-permissions-detail'),
    

    
    # Separate Admin Creation URLs (Super Admin only)
    path('admin/create/', CreateAdminView.as_view(), name='create-admin'),
    path('admin/create-accountant/', CreateAccountantView.as_view(), name='create-accountant'),
    path('admin/create-support/', CreateSupportManagerView.as_view(), name='create-support-manager'),

    
    # CRUD URLs for each role (Super Admin only)
    path('accountant/', AccountantCRUDView.as_view(), name='accountant-crud'),
    path('support-manager/', SupportManagerCRUDView.as_view(), name='support-manager-crud'),

]
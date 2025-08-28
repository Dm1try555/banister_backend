from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, RefreshTokenView, ProfileView,
    SendVerificationEmailView, VerifyEmailView,
    PasswordResetRequestView, PasswordResetConfirmView,
    AdminUserViewSet, ProfilePhotoUploadView, DeleteProfileView,
    admin_permission_list, admin_permission_detail, admin_permission_by_admin,
    admin_user_register, admin_login
)
from .views.fcm_token_views import (
    FCMTokenRegisterView, FCMTokenUnregisterView, FCMTokenListView
)

router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh_token'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/profile/delete/', DeleteProfileView.as_view(), name='delete_profile'),
    path('auth/send-verification/', SendVerificationEmailView.as_view(), name='send_verification_email'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('auth/password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/upload-photo/', ProfilePhotoUploadView.as_view(), name='upload_profile_photo'),
    
    # Admin Authentication URLs
    path('admin/register/', admin_user_register, name='admin_user_register'),
    path('admin/login/', admin_login, name='admin_login'),
    
    # Admin Permission Management URLs
    path('admin/permissions/', admin_permission_list, name='admin_permission_list'),
    path('admin/permissions/<int:pk>/', admin_permission_detail, name='admin_permission_detail'),
    path('admin/permissions/by-admin/<int:admin_id>/', admin_permission_by_admin, name='admin_permission_by_admin'),
    
    # FCM Token Management URLs
    path('auth/fcm-token/register/', FCMTokenRegisterView.as_view(), name='fcm-token-register'),
    path('auth/fcm-token/unregister/', FCMTokenUnregisterView.as_view(), name='fcm-token-unregister'),
    path('auth/fcm-token/list/', FCMTokenListView.as_view(), name='fcm-token-list'),
] + router.urls
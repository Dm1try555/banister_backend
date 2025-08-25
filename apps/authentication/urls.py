from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, RefreshTokenView, ProfileView,
    SendVerificationEmailView, VerifyEmailView,
    PasswordResetRequestView, PasswordResetConfirmView,
    AdminUserViewSet, ProfilePhotoUploadView
)

router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh_token'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/send-verification/', SendVerificationEmailView.as_view(), name='send_verification_email'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('auth/password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('auth/upload-photo/', ProfilePhotoUploadView.as_view(), name='upload_profile_photo'),
] + router.urls
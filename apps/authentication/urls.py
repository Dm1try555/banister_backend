from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, register, login, refresh_token, profile,
    send_verification_email, verify_email,
    update_admin_profile, manage_admin_permissions, get_admin_permissions,
    upload_profile_photo
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/refresh/', refresh_token, name='refresh_token'),
    path('auth/profile/', profile, name='profile'),
    path('auth/send-verification/', send_verification_email, name='send_verification_email'),
    path('auth/verify-email/', verify_email, name='verify_email'),
    path('auth/admin/update-profile/', update_admin_profile, name='update_admin_profile'),
    path('auth/admin/manage-permissions/', manage_admin_permissions, name='manage_admin_permissions'),
    path('auth/admin/permissions/', get_admin_permissions, name='get_admin_permissions'),
    path('auth/upload-photo/', upload_profile_photo, name='upload_profile_photo'),
] + router.urls
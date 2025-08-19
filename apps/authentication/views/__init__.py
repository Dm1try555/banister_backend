from .user_views import UserViewSet
from .auth_views import register, login, refresh_token, profile
from .email_views import send_verification_email, verify_email
from .admin_views import update_admin_profile, manage_admin_permissions, get_admin_permissions
from .profile_photo_views import upload_profile_photo

__all__ = [
    'UserViewSet',
    'register', 'login', 'refresh_token', 'profile',
    'send_verification_email', 'verify_email',
    'update_admin_profile', 'manage_admin_permissions', 'get_admin_permissions',
    'upload_profile_photo'
]
# Import all views from the new modular structure
from .views.registration import (
    CustomerRegistrationView,
    ProviderRegistrationView,
    ManagementRegistrationView,
    FirebaseAuthView
)

from .views.login import (
    CustomerLoginView,
    ProviderLoginView,
    ManagementLoginView,
    AdminLoginView,
    SuperAdminLoginView,
    AccountantLoginView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView
)

from .views.profile import (
    ProfileView
)

from .views.password import (
    password_reset_request,
    password_reset_confirm,
    logout_view,
    email_confirm_request,
    email_confirm_verify
)

from .views.admin import (
    AdminProfileView,
    AdminPermissionManagementView
)

from .views.mixins import (
    VerificationCodeSenderMixin,
    VerificationCodeVerifyMixin
)

# Export all views for backward compatibility
__all__ = [
    # Registration
    'CustomerRegistrationView',
    'ProviderRegistrationView', 
    'ManagementRegistrationView',
    'FirebaseAuthView',
    
    # Login
    'CustomerLoginView',
    'ProviderLoginView',
    'ManagementLoginView',
    'AdminLoginView',
    'SuperAdminLoginView',
    'AccountantLoginView',
    'CustomTokenObtainPairView',
    'CustomTokenRefreshView',
    
    # Profile
    'ProfileView',
    
    # Password
    'password_reset_request',
    'password_reset_confirm',
    'logout_view',
    'email_confirm_request',
    'email_confirm_verify',
    
    # Admin
    'AdminProfileView',
    'AdminPermissionManagementView',
    
    # Mixins
    'VerificationCodeSenderMixin',
    'VerificationCodeVerifyMixin'
]

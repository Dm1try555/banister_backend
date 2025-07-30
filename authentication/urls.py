from django.urls import path
from .views import (
    register_customer, register_provider, register_management,
    CustomTokenObtainPairView, ProfileView,
    PasswordResetView, logout_view,
    CustomerLoginView, ProviderLoginView, ManagementLoginView,
    email_confirm_request, email_confirm_verify
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/customer/', register_customer, name='register-customer'),
    path('register/provider/', register_provider, name='register-provider'),
    path('register/management/', register_management, name='register-management'),
    path('login/customer/', CustomerLoginView.as_view(), name='login-customer'),
    path('login/provider/', ProviderLoginView.as_view(), name='login-provider'),
    path('login/management/', ManagementLoginView.as_view(), name='login-management'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # path('password-reset/', PasswordResetView.as_view(), name='password-reset'),  # optional
]

urlpatterns += [
    # Email confirmation
    path('email-confirm/request/', email_confirm_request, name='email_confirm_request'),
    path('email-confirm/verify/', email_confirm_verify, name='email_confirm_verify'),
]
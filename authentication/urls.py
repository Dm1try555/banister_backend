# authentication/urls.py
from django.urls import path
from .views import (
    CustomerRegistrationView, ProviderRegistrationView, ManagementRegistrationView,
    CustomTokenObtainPairView, ProfileView,
    password_reset_request, password_reset_confirm, logout_view,
    CustomerLoginView, ProviderLoginView, ManagementLoginView,
    CustomTokenRefreshView, email_confirm_request, email_confirm_verify
)

urlpatterns = [
    path('register/customer/', CustomerRegistrationView.as_view(), name='register-customer'),
    path('register/provider/', ProviderRegistrationView.as_view(), name='register-provider'),
    path('register/management/', ManagementRegistrationView.as_view(), name='register-management'),
    path('login/customer/', CustomerLoginView.as_view(), name='login-customer'),
    path('login/provider/', ProviderLoginView.as_view(), name='login-provider'),
    path('login/management/', ManagementLoginView.as_view(), name='login-management'),
    path('logout/', logout_view, name='logout'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-reset/request/', password_reset_request, name='password-reset-request'),
    path('password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
]

urlpatterns += [
    path('email-confirm/request/', email_confirm_request, name='email_confirm_request'),
    path('email-confirm/verify/', email_confirm_verify, name='email_confirm_verify'),
]
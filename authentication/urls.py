from django.urls import path
from .views import (
    RegisterCustomerView, RegisterProviderView, QuickRegisterView,
    FirebaseAuthView, CustomTokenObtainPairView, ProfileView,
    PasswordResetView, LogoutView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/customer', RegisterCustomerView.as_view(), name='register-customer'),
    path('register/provider', RegisterProviderView.as_view(), name='register-provider'),
    path('register/quick/customer', QuickRegisterView.as_view(), {'role': 'customer'}, name='quick-register-customer'),
    path('register/quick/provider', QuickRegisterView.as_view(), {'role': 'provider'}, name='quick-register-provider'),
    path('register/google', FirebaseAuthView.as_view(), {'provider': 'google'}, name='google-auth'),
    path('register/apple', FirebaseAuthView.as_view(), {'provider': 'apple'}, name='apple-auth'),
    path('login', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('password-reset', PasswordResetView.as_view(), name='password-reset'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile', ProfileView.as_view(), name='profile'),
]
from django.urls import path
from .views import (
    RegisterCustomerView, RegisterProviderView,
    CustomTokenObtainPairView, ProfileView,
    PasswordResetView, LogoutView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/customer/', RegisterCustomerView.as_view(), name='register-customer'),
    path('register/provider/', RegisterProviderView.as_view(), name='register-provider'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # path('password-reset/', PasswordResetView.as_view(), name='password-reset'),  # опционально
]
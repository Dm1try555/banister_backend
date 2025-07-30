from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Banister API",
        default_version='v1',
        description="API for Banister project",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication and profile
    path('api/v1/auth/', include('authentication.urls')),

    # Bookings
    path('api/v1/bookings/', include('bookings.urls')),

    # Services
    path('api/v1/services/', include('services.urls')),

    # Payments
    path('api/v1/payments/', include('payments.urls')),

    # Withdrawals
    path('api/v1/withdrawals/', include('withdrawals.urls')),

    # Messages and chats
    path('api/v1/message/', include('message.urls')),

    # Schedule
    path('api/v1/schedules/', include('schedules.urls')),

    # Documents
    path('api/v1/documents/', include('documents.urls')),

    # Admin panel
    path('api/v1/users/', include('admin_panel.urls')),

    # Dashboard
    path('api/v1/dashboard/', include('dashboard.urls')),

    # Public services
    path('api/v1/public/', include('public_core.urls')),

    # File storage
    path('api/v1/files/', include('file_storage.urls')),

    # swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
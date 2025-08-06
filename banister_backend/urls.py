from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Banister API v1",
        default_version='v1',
        description="""
        ## Banister Project API
        
        ### Authentication
        Use JWT tokens for authentication. In the Authorization field, insert only the token (without "Bearer").
        The system will automatically add "Bearer " to your token.
        
        ### Usage Examples:
        1. Get a token through `/api/v1/auth/login/customer/` or `/api/v1/auth/login/provider/`
        2. Copy the `access` value from the response
        3. Insert the token in the Authorization field in Swagger UI
        4. Now you can use protected endpoints
        
        ### Supported Roles:
        - **customer** - customers
        - **provider** - service providers  
        - **management** - managers
        - **admin** - administrators
        - **super_admin** - super administrators
        - **accountant** - accountants
        
        ### Base URL: localhost:8000/api/v1
        """,
        terms_of_service="Terms of service",
        contact=openapi.Contact(email="Contact the developer"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Authentication and profile
    path('api/v1/auth/', include('core.authentication.urls')),

    # Bookings
    path('api/v1/bookings/', include('apps.bookings.urls')),

    # Services
    path('api/v1/services/', include('apps.services.urls')),

    # Payments
    path('api/v1/payments/', include('apps.payments.urls')),

    # Withdrawals
    path('api/v1/withdrawals/', include('apps.withdrawals.urls')),

    # Messages and chats
    path('api/v1/message/', include('apps.message.urls')),

    # Schedule
    path('api/v1/schedules/', include('apps.schedules.urls')),

    # Documents
    path('api/v1/documents/', include('apps.documents.urls')),

    # Admin panel
    path('api/v1/users/', include('apps.admin_panel.urls')),

    # Dashboard
    path('api/v1/dashboard/', include('apps.dashboard.urls')),

    # Public services
    path('api/v1/public/', include('public_core.urls')),

    # File storage
    path('api/v1/files/', include('core.file_storage.urls')),

    # Workers
    path('api/v1/workers/', include('core.workers.urls')),

    # Notifications
    path('api/v1/notifications/', include('apps.notifications.urls')),

    # swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
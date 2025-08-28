from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# API info for Swagger settings
api_info = openapi.Info(
    title="Banister API",
    default_version='v1',
)

def get_api_patterns():
    """Returns API URL patterns for reuse"""
    return [
        path('', include('apps.authentication.urls')),
        path('', include('apps.bookings.urls')),
        path('', include('apps.services.urls')),
        path('', include('apps.payments.urls')),
        path('', include('apps.withdrawals.urls')),
        path('', include('apps.documents.urls')),
        path('', include('apps.dashboard.urls')),
        path('', include('apps.notifications.urls')),
        path('chat/', include('apps.chat.urls')),
        path('', include('apps.interviews.urls')),
    ]

# Create schema view once
schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/v1/', include(get_api_patterns())),
    ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/v1/', include(get_api_patterns())),
]
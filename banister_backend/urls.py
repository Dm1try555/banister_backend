from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response

# API info для настроек Swagger
api_info = openapi.Info(
    title="Banister API",
    default_version='v1',
    description="API для платформы бронирования услуг",
    terms_of_service="https://www.banister.com/terms/",
    contact=openapi.Contact(email="contact@banister.com"),
    license=openapi.License(name="MIT License"),
)

# Простой тестовый view для Swagger
@api_view(['GET'])
def test_view(request):
    return Response({'message': 'Test endpoint working'})

schema_view = get_schema_view(
    api_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=[
        path('api/v1/', include([
            path('', include('apps.authentication.urls')),
            path('', include('apps.bookings.urls')),
            path('', include('apps.services.urls')),
            path('', include('apps.payments.urls')),
            path('', include('apps.withdrawals.urls')),
            path('', include('apps.documents.urls')),
            path('', include('apps.dashboard.urls')),
            path('', include('apps.notifications.urls')),
            path('chat/', include('apps.chat.urls')),
        ])),
    ],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Тестовый endpoint
    path('test/', test_view, name='test'),
    
    # API endpoints
    path('api/v1/', include([
        # Apps
        path('', include('apps.authentication.urls')),
        path('', include('apps.bookings.urls')),
        path('', include('apps.services.urls')),
        path('', include('apps.payments.urls')),
        path('', include('apps.withdrawals.urls')),
        path('', include('apps.documents.urls')),
        path('', include('apps.dashboard.urls')),
        path('', include('apps.notifications.urls')),
        path('chat/', include('apps.chat.urls')),
    ])),
]
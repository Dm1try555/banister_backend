from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Banister API",
        default_version='v1',
        description="API для платформы бронирования услуг",
        terms_of_service="https://www.banister.com/terms/",
        contact=openapi.Contact(email="contact@banister.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    
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
        path('', include('apps.message.urls')),
    ])),
    
    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
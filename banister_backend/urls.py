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

    # api
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/public/', include('public_core.urls')),
    path('api/v1/bookings/', include('bookings.urls')),
    path('api/v1/services/', include('services.urls')),
    path('api/v1/schedule/', include('schedules.urls')),
    path('api/v1/message/', include('message.urls')),
    path('api/v1/payments/', include('payments.urls')),
    path('api/v1/withdrawals/', include('withdrawals.urls')),
    path('api/v1/dashboard/', include('dashboard.urls')),
    path('api/v1/admin/', include('admin_panel.urls')),

    # swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
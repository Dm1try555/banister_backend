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

    # Аутентификация и профиль
    path('api/v1/auth/', include('authentication.urls')),

    # Пользователи и роли
    path('api/v1/users/', include('admin_panel.urls')),

    # Бронирования
    path('api/v1/bookings/', include('bookings.urls')),

    # Услуги
    path('api/v1/services/', include('services.urls')),

    # Сообщения
    path('api/v1/message/', include('message.urls')),

    # Платежи и история
    path('api/v1/payments/', include('payments.urls')),
    path('api/v1/withdrawals/', include('withdrawals.urls')),

    # Документы
    path('api/v1/documents/', include('documents.urls')),

    # Управление (management)
    # path('api/v1/management/', include('management.urls')),  # заглушка, если потребуется отдельное приложение

    # Календарь
    path('api/v1/schedule/', include('schedules.urls')),

    # Дашборд
    path('api/v1/dashboard/', include('dashboard.urls')),

    # Публичные сервисы
    path('api/v1/public/', include('public_core.urls')),

    # swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
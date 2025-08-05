from django.urls import path
from .views import (
    BookingListView, BookingCreateView, BookingDetailView, 
    BookingStatusUpdateView, ProviderSearchView,
    GoogleMeetInvitationView
)

urlpatterns = [
    # Поиск провайдеров
    path('search/', ProviderSearchView.as_view(), name='provider-search'),
    
    # Основные операции с бронированиями
    path('', BookingListView.as_view(), name='booking-list'),
    path('create/', BookingCreateView.as_view(), name='booking-create'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:booking_id>/status/', BookingStatusUpdateView.as_view(), name='booking-status-update'),
    
    # Тестовый эндпоинт для Google Meet приглашений
    path('google-meet-invitation/', GoogleMeetInvitationView.as_view(), name='google-meet-invitation'),
]
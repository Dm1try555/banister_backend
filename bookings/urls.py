from django.urls import path
from .views import (
    BookingListView, BookingCreateView, BookingDetailView, 
    BookingStatusUpdateView, ProviderSearchView,
    SendMeetingInvitationView, AdminSendMeetingInvitationView
)

urlpatterns = [
    # Поиск провайдеров
    path('search/', ProviderSearchView.as_view(), name='provider-search'),
    
    # Основные операции с бронированиями
    path('', BookingListView.as_view(), name='booking-list'),
    path('create/', BookingCreateView.as_view(), name='booking-create'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:booking_id>/status/', BookingStatusUpdateView.as_view(), name='booking-status-update'),
    
    # Отправка приглашений на встречи
    path('<int:booking_id>/send-invitation/', SendMeetingInvitationView.as_view(), name='send-meeting-invitation'),
    path('<int:booking_id>/admin/send-invitation/', AdminSendMeetingInvitationView.as_view(), name='admin-send-meeting-invitation'),
]
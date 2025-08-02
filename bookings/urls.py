from django.urls import path
from .views import (
    BookingListView, BookingCreateView, BookingDetailView, BookingStatusUpdateView,
    ProviderSearchView
)

urlpatterns = [
    # Main booking endpoints - only 6 methods
    path('', BookingListView.as_view(), name='booking-list'),  # GET /bookings/
    path('create/', BookingCreateView.as_view(), name='booking-create'),  # POST /bookings/create/
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),  # GET/PUT /bookings/{id}/
    path('<int:booking_id>/status/', BookingStatusUpdateView.as_view(), name='booking-status-update'),  # POST /bookings/{booking_id}/status/
    
    # Provider search
    path('provider-search/', ProviderSearchView.as_view(), name='provider-search'),  # GET /bookings/provider-search/
]
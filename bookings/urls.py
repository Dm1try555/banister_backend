from django.urls import path
from .views import BookingListCreateView, BookingDetailView, BookingStatusUpdateView

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list-create'),  # GET/POST /api/v1/bookings/
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),  # GET/PUT/PATCH/DELETE /api/v1/bookings/{id}/
    path('status/<int:booking_id>/', BookingStatusUpdateView.as_view(), name='booking-status-update'),  # POST /api/v1/bookings/status/{booking_id}/
]
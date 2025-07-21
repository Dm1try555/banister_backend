from django.urls import path
from .views import BookingCreateView, BookingListView, BookingDetailView

urlpatterns = [
    path('', BookingListView.as_view(), name='booking-list'),  # GET /api/v1/bookings/
    path('', BookingCreateView.as_view(), name='booking-create'),  # POST /api/v1/bookings/
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),  # GET/PUT/PATCH/DELETE /api/v1/bookings/{id}/
]
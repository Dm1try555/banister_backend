from django.urls import path
from .views import (
    InterviewListCreateView, InterviewDetailView,
    BookingListCreateView, BookingDetailView
)

urlpatterns = [
    # Interview URLs
    path('interviews/', InterviewListCreateView.as_view(), name='interview-list-create'),
    path('interviews/<int:pk>/', InterviewDetailView.as_view(), name='interview-detail'),
    
    # Booking URLs
    path('bookings/', BookingListCreateView.as_view(), name='booking-list-create'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
]
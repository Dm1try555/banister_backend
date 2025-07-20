from django.urls import path
from .views import BookingCreateView, BookingListView, BookingDetailView

urlpatterns = [
    path('', BookingCreateView.as_view(), name='booking-create'),
    path('', BookingListView.as_view(), name='booking-list'),
    path('<int:pk>', BookingDetailView.as_view(), name='booking-detail'),
]
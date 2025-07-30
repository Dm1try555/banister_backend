from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import DashboardStats
from .serializers import DashboardStatsSerializer
from bookings.models import Booking
from payments.models import Payment
from django.db import transaction

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    PermissionError, ValidationError, NotFoundError
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class DashboardOverviewView(BaseAPIView, generics.RetrieveAPIView):
    """User dashboard overview"""
    serializer_class = DashboardStatsSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get_object(self):
        stats, _ = DashboardStats.objects.get_or_create(user=self.request.user)
        return stats

class DashboardStatisticsView(BaseAPIView, generics.RetrieveAPIView):
    """Dashboard statistics with booking and earnings calculation"""
    serializer_class = DashboardStatsSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get_object(self):
        if self.request.user.role == 'customer':
            bookings = Booking.objects.filter(customer=self.request.user).count()
            earnings = 0
        elif self.request.user.role == 'provider':
            bookings = Booking.objects.filter(provider=self.request.user).count()
            earnings = sum(p.amount for p in Payment.objects.filter(user=self.request.user, status='completed'))
        else:
            raise PermissionError('Unknown user role')
        stats, _ = DashboardStats.objects.get_or_create(user=self.request.user)
        stats.total_bookings = bookings
        stats.total_earnings = earnings
        stats.save()
        return stats
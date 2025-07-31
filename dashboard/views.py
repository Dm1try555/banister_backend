from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import DashboardStats
from .serializers import DashboardStatsSerializer
from bookings.models import Booking
from payments.models import Payment
from authentication.models import User
from django.db import transaction

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    CustomPermissionError, ValidationError, NotFoundError
)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

class DashboardOverviewView(BaseAPIView):
    """User dashboard overview"""
    serializer_class = DashboardStatsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        try:
            logger.info(f"Dashboard overview requested by user: {request.user.email} with role: {request.user.role}")
            
            # Calculate current statistics
            if request.user.role == 'customer':
                bookings = Booking.objects.filter(customer=request.user).count()
                earnings = 0
            elif request.user.role == 'provider':
                bookings = Booking.objects.filter(provider=request.user).count()
                earnings = sum(p.amount for p in Payment.objects.filter(user=request.user, status='completed'))
            elif request.user.role == 'management':
                # Management can see all bookings and total earnings
                bookings = Booking.objects.count()
                earnings = sum(p.amount for p in Payment.objects.filter(status='completed'))
            else:
                logger.error(f"Unknown user role: {request.user.role}")
                raise CustomPermissionError('Unknown user role')
            
            logger.info(f"Calculated stats - bookings: {bookings}, earnings: {earnings}")
            
            # Update or create stats
            stats, _ = DashboardStats.objects.get_or_create(user=request.user)
            stats.total_bookings = bookings
            stats.total_earnings = earnings
            stats.save()
            
            serializer = self.get_serializer(stats)
            logger.info("Dashboard overview response prepared successfully")
            return self.success_response(data=serializer.data)
            
        except Exception as e:
            logger.error(f"Error in dashboard overview: {str(e)}", exc_info=True)
            raise

class DashboardStatisticsView(BaseAPIView):
    """Dashboard statistics with booking and earnings calculation"""
    serializer_class = DashboardStatsSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

# Удалены все тестовые views

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        try:
            logger.info(f"Dashboard statistics requested by user: {request.user.email} with role: {request.user.role}")
            
            if request.user.role == 'customer':
                bookings = Booking.objects.filter(customer=request.user).count()
                earnings = 0
            elif request.user.role == 'provider':
                bookings = Booking.objects.filter(provider=request.user).count()
                earnings = sum(p.amount for p in Payment.objects.filter(user=request.user, status='completed'))
            elif request.user.role == 'management':
                # Management can see all bookings and total earnings
                bookings = Booking.objects.count()
                earnings = sum(p.amount for p in Payment.objects.filter(status='completed'))
            else:
                logger.error(f"Unknown user role: {request.user.role}")
                raise CustomPermissionError('Unknown user role')
            
            logger.info(f"Calculated stats - bookings: {bookings}, earnings: {earnings}")
            
            stats, _ = DashboardStats.objects.get_or_create(user=request.user)
            stats.total_bookings = bookings
            stats.total_earnings = earnings
            stats.save()
            
            serializer = self.get_serializer(stats)
            logger.info("Dashboard statistics response prepared successfully")
            return self.success_response(data=serializer.data)
            
        except Exception as e:
            logger.error(f"Error in dashboard statistics: {str(e)}", exc_info=True)
            raise
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import DashboardStats
from .serializers import DashboardStatsSerializer
from apps.bookings.models import Booking
from apps.payments.models import Payment
from core.authentication.models import User
from django.db import transaction

# Import error handling system
from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)

class DashboardView(BaseAPIView):
    """User dashboard overview and statistics"""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']  # Только GET
    
    @swagger_auto_schema(
        operation_description="Get dashboard overview and statistics",
        responses={200: openapi.Response('Dashboard data', DashboardStatsSerializer)},
        tags=['Dashboard']
    )
    def get(self, request):
        """Получить данные дашборда"""
        try:
            logger.info(f"Dashboard requested by user: {request.user.email} with role: {request.user.role}")
            
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
                return self.error_response(
                    error_number='UNKNOWN_ROLE',
                    error_message='Unknown user role',
                    status_code=400
                )
            
            logger.info(f"Calculated stats - bookings: {bookings}, earnings: {earnings}")
            
            # Update or create stats
            stats, _ = DashboardStats.objects.get_or_create(user=request.user)
            stats.total_bookings = bookings
            stats.total_earnings = earnings
            stats.save()
            
            serializer = DashboardStatsSerializer(stats)
            logger.info("Dashboard response prepared successfully")
            return self.success_response(
                data=serializer.data,
                message='Данные дашборда получены'
            )
            
        except Exception as e:
            logger.error(f"Error in dashboard: {str(e)}", exc_info=True)
            return self.error_response(
                error_number='DASHBOARD_ERROR',
                error_message=f'Ошибка получения данных дашборда: {str(e)}',
                status_code=500
            )
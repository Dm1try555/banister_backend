from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DashboardStats
from .serializers import DashboardStatsSerializer
from bookings.models import Booking
from payments.models import Payment

class DashboardOverviewView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        stats, created = DashboardStats.objects.get_or_create(user=request.user)
        return Response(DashboardStatsSerializer(stats).data)

class DashboardStatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        bookings = Booking.objects.filter(customer=request.user).count()
        earnings = sum(p.amount for p in Payment.objects.filter(user=request.user, status='completed'))
        stats, created = DashboardStats.objects.get_or_create(user=request.user)
        stats.total_bookings = bookings
        stats.total_earnings = earnings
        stats.save()
        return Response(DashboardStatsSerializer(stats).data)
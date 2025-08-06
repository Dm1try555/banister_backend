from rest_framework import serializers
from .models import DashboardStats
from core.authentication.serializers import UserSerializer

class DashboardStatsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = DashboardStats
        fields = ['user', 'total_bookings', 'total_earnings']
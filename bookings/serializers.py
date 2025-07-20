from rest_framework import serializers
from .models import Booking
from authentication.serializers import UserSerializer
from services.serializers import ServiceSerializer

class BookingSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    provider = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'customer', 'service', 'provider', 'date', 'status', 'created_at']
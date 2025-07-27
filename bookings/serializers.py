from rest_framework import serializers
from .models import Booking
from authentication.serializers import UserSerializer
from services.serializers import ServiceSerializer
from authentication.models import User
from services.models import Service

class BookingSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    provider = UserSerializer(read_only=True)
    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='provider'), write_only=True, source='provider'
    )
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), write_only=True, source='service'
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'provider', 'provider_id',
            'service', 'service_id', 'date', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'customer', 'provider', 'service', 'created_at']
        
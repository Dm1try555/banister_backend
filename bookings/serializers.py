from rest_framework import serializers
from .models import Booking
from authentication.models import User
from services.models import Service

class BookingSerializer(serializers.ModelSerializer):
    # Read-only fields for display
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)
    provider_id = serializers.IntegerField(source='provider.id', read_only=True)
    service_id = serializers.IntegerField(source='service.id', read_only=True)
    
    # Write-only fields for creation/update
    service = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), 
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'customer_id', 'provider_id', 'service_id',
            'service', 'date', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'customer_id', 'provider_id', 'service_id', 'created_at']
        
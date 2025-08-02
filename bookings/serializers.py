from rest_framework import serializers
from .models import Booking
from services.models import Service
from authentication.models import User

class BookingSerializer(serializers.ModelSerializer):
    # Read-only fields for display
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)
    provider_id = serializers.IntegerField(source='provider.id', read_only=True)
    service_id = serializers.IntegerField(source='service.id', read_only=True)
    service_title = serializers.CharField(source='service.title', read_only=True)
    provider_name = serializers.CharField(source='provider.get_full_name', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'customer_id', 'provider_id', 'service_id', 'service_title', 'provider_name',
            'location', 'preferred_date', 'preferred_time', 'frequency', 'scheduled_datetime',
            'status', 'notes', 'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'customer_id', 'provider_id', 'service_id', 'service_title', 
                           'provider_name', 'total_price', 'created_at']

class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings with validation"""
    
    class Meta:
        model = Booking
        fields = [
            'service', 'location', 'preferred_date', 'preferred_time', 'frequency', 'notes'
        ]
    
    def validate(self, data):
        # Validate that the service exists and is active
        service = data.get('service')
        if not service:
            raise serializers.ValidationError("Service is required")
        
        # Validate preferred date is not in the past
        from datetime import date
        if data.get('preferred_date') and data['preferred_date'] < date.today():
            raise serializers.ValidationError("Preferred date cannot be in the past")
        
        return data

class BookingUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating bookings"""
    
    class Meta:
        model = Booking
        fields = [
            'location', 'preferred_date', 'preferred_time', 'frequency', 'notes'
        ]
    
    def validate(self, data):
        # Validate preferred date is not in the past
        from datetime import date
        if data.get('preferred_date') and data['preferred_date'] < date.today():
            raise serializers.ValidationError("Preferred date cannot be in the past")
        
        return data

class BookingStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating booking status"""
    status = serializers.ChoiceField(
        choices=Booking.STATUS_CHOICES,
        help_text="New booking status"
    )

class ServiceSearchSerializer(serializers.ModelSerializer):
    """Serializer for service search results"""
    provider_name = serializers.CharField(source='provider.get_full_name', read_only=True)
    provider_rating = serializers.SerializerMethodField()
    provider_reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'title', 'description', 'price', 'provider_name', 
                 'provider_rating', 'provider_reviews_count', 'created_at']
    
    def get_provider_rating(self, obj):
        # Placeholder for provider rating calculation
        return 4.5  # This would be calculated from reviews
    
    def get_provider_reviews_count(self, obj):
        # Placeholder for provider reviews count
        return 12  # This would be calculated from reviews

class ProviderSearchRequestSerializer(serializers.Serializer):
    """Serializer for provider search request"""
    service_type = serializers.CharField(
        required=False, 
        help_text="Type of service (e.g., 'maid', 'gardener', 'chef')"
    )
    location = serializers.CharField(
        required=False, 
        help_text="Service location/address"
    )
    preferred_date = serializers.DateField(
        required=False, 
        help_text="Preferred service date (YYYY-MM-DD)"
    )
    preferred_time = serializers.TimeField(
        required=False, 
        help_text="Preferred service time (HH:MM)"
    )
    frequency = serializers.ChoiceField(
        choices=Booking.FREQUENCY_CHOICES, 
        default='one_time',
        help_text="Service frequency"
    )
    max_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        help_text="Maximum price willing to pay"
    )
        
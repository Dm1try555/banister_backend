from core.base.common_imports import *
from core.error_handling import ErrorCode

from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'customer', 'service', 'provider', 'location', 
            'preferred_date', 'preferred_time', 'scheduled_datetime', 
            'status', 'notes', 'total_price', 'created_at'
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['service', 'preferred_date', 'preferred_time', 'notes']

    def validate_preferred_date(self, value):
        if value < timezone.now().date():
            ErrorCode.INVALID_BOOKING_TIME.raise_error()
        return value

    def validate_preferred_time(self, value):
        if value:
            current_time = timezone.now().time()
            if timezone.now().date() == self.initial_data.get('preferred_date') and value < current_time:
                ErrorCode.INVALID_BOOKING_TIME.raise_error()
        return value


class BookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status', 'scheduled_datetime', 'notes', 'total_price']

    def validate_status(self, value):
        if value not in ['pending', 'confirmed', 'completed', 'cancelled']:
            ErrorCode.INVALID_BOOKING_STATUS.raise_error()
        return value

    def validate_total_price(self, value):
        if value and value <= 0:
            ErrorCode.INVALID_SERVICE_PRICE.raise_error()
        return value
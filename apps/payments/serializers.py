from core.base.common_imports import *
from core.error_handling import ErrorCode

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    # Add computed fields for service and currency
    service = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'customer', 'provider', 'service', 'amount', 'currency',
            'status', 'stripe_payment_intent_id', 'stripe_transfer_id',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['customer', 'provider', 'created_at', 'completed_at']
    
    def get_service(self, obj):
        """Get service through booking"""
        return obj.booking.service.id if obj.booking and obj.booking.service else None
    
    def get_currency(self, obj):
        """Default USD for all payments"""
        return 'USD'


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments"""
    # Add computed fields for service and currency
    service_title = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'amount', 'currency', 'status', 'stripe_payment_intent_id', 'service_title',
            'created_at'
        ]
        read_only_fields = ['id', 'status', 'stripe_payment_intent_id', 'created_at']
    
    def get_service_title(self, obj):
        """Get service title through booking"""
        return obj.booking.service.title if obj.booking and obj.booking.service else None
    
    def get_currency(self, obj):
        """Get currency through booking"""
        return obj.booking.service.currency if obj.booking and obj.booking.service else 'USD'
    
    def validate(self, attrs):
        """Validate payment data"""
        booking = attrs.get('booking')
        amount = attrs.get('amount')
        
        if not booking:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        
        # Automatically set customer and provider from booking
        attrs['customer'] = booking.customer
        attrs['provider'] = booking.service.provider
        
        # Check that amount matches service price
        if amount != booking.service.price:
            ErrorCode.PAYMENT_AMOUNT_INVALID.raise_error()
        
        return attrs
    
    def validate_amount(self, value):
        """Validate payment amount"""
        # Check that amount is positive
        if value <= 0:
            ErrorCode.PAYMENT_AMOUNT_INVALID.raise_error()
        return value


class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['status', 'stripe_payment_intent_id']
        read_only_fields = ['booking', 'customer', 'provider', 'amount']


class PaymentConfirmSerializer(serializers.Serializer):
    payment_intent_id = serializers.CharField()


class PaymentTransferSerializer(serializers.Serializer):
    provider_stripe_account = serializers.CharField()
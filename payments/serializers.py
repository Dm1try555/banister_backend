from rest_framework import serializers
from .models import Payment
from bookings.models import Booking
from authentication.models import User

class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для платежей"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    booking_title = serializers.CharField(source='booking.service.title', read_only=True)
    formatted_amount = serializers.CharField(source='get_formatted_amount', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'user_name', 'booking', 'booking_title',
            'amount', 'currency', 'formatted_amount', 'status', 'payment_method',
            'payment_method_display', 'created_at', 'updated_at', 'completed_at',
            'transaction_id', 'description', 'is_successful', 'is_pending', 'is_failed'
        ]
        read_only_fields = [
            'id', 'user_email', 'user_name', 'booking_title', 'formatted_amount',
            'payment_method_display', 'created_at', 'updated_at', 'completed_at',
            'is_successful', 'is_pending', 'is_failed'
        ]

class StripePaymentIntentSerializer(serializers.Serializer):
    """Сериализатор для создания Payment Intent в Stripe"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    currency = serializers.ChoiceField(choices=Payment.CURRENCY_CHOICES, default='usd')
    booking_id = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)

class StripePaymentConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения платежа в Stripe"""
    payment_intent_id = serializers.CharField(max_length=255)
    booking_id = serializers.IntegerField(required=False, allow_null=True)

class StripeCustomerSerializer(serializers.Serializer):
    """Сериализатор для создания клиента в Stripe"""
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)

class StripePaymentMethodSerializer(serializers.Serializer):
    """Сериализатор для привязки метода оплаты"""
    payment_method_id = serializers.CharField(max_length=255)
    customer_id = serializers.CharField(max_length=255)

class PaymentStatusSerializer(serializers.Serializer):
    """Сериализатор для статуса платежа"""
    payment_intent_id = serializers.CharField(max_length=255)

class PaymentRefundSerializer(serializers.Serializer):
    """Сериализатор для возврата средств"""
    payment_intent_id = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
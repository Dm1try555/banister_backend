from rest_framework import serializers
from .models import Payment
from authentication.serializers import UserSerializer

class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'status', 'created_at']
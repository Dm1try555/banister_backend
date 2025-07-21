from rest_framework import serializers
from .models import Withdrawal
from authentication.serializers import UserSerializer

class WithdrawalSerializer(serializers.ModelSerializer):
    provider = UserSerializer(read_only=True)
    class Meta:
        model = Withdrawal
        fields = ['id', 'provider', 'amount', 'status', 'created_at']
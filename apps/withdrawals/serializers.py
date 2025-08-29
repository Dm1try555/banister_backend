from core.base.common_imports import *
from core.error_handling import ErrorCode

from .models import Withdrawal


class WithdrawalSerializer(OptimizedModelSerializer):
    class Meta:
        model = Withdrawal
        fields = [
            'id', 'user', 'amount', 'currency', 'status', 'stripe_transfer_id',
            'reason', 'created_at', 'completed_at'
        ]


class WithdrawalCreateSerializer(OptimizedModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['amount', 'currency']

    def validate_amount(self, value):
        if value <= 0:
            ErrorCode.WITHDRAWAL_AMOUNT_TOO_SMALL.raise_error()
        
        if value < 10:  # Minimum withdrawal amount
            ErrorCode.WITHDRAWAL_AMOUNT_TOO_SMALL.raise_error()
        
        if value > 10000:  # Maximum withdrawal amount
            ErrorCode.WITHDRAWAL_LIMIT_EXCEEDED.raise_error()
        
        return value


class WithdrawalUpdateSerializer(OptimizedModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['status', 'stripe_transfer_id', 'completed_at', 'reason']


class WithdrawalApproveSerializer(OptimizedModelSerializer):
    class Meta:
        model = Withdrawal
        fields = []


class WithdrawalRejectSerializer(OptimizedModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['reason']

    def validate_reason(self, value):
        if not value or len(value.strip()) < 10:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        return value
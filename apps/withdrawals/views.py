from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Withdrawal
from .serializers import WithdrawalSerializer
from core.stripe.service import stripe_service
from core.base.views import BaseModelViewSet

class WithdrawalViewSet(BaseModelViewSet):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        withdrawal = self.get_object()
        
        if withdrawal.status != 'pending':
            return Response({
                'error': 'Withdrawal already processed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user_stripe_account = withdrawal.user.stripe_account_id
        if not user_stripe_account:
            return Response({
                'error': 'User Stripe account not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success, result = stripe_service.transfer_to_account(
            amount=withdrawal.amount,
            destination_account=user_stripe_account,
            metadata={
                'withdrawal_id': withdrawal.id,
                'user_id': withdrawal.user.id
            }
        )
        
        if success:
            withdrawal.status = 'completed'
            withdrawal.completed_at = timezone.now()
            withdrawal.stripe_transfer_id = result.id
            withdrawal.save()
            
            return Response({
                'status': 'withdrawal approved and transferred'
            })
        else:
            return Response({
                'error': result
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        withdrawal = self.get_object()
        withdrawal.status = 'rejected'
        withdrawal.save()
        
        return Response({'status': 'withdrawal rejected'})
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Payment
from .serializers import PaymentSerializer
from core.stripe.service import stripe_service
from core.base.views import BaseModelViewSet

class PaymentViewSet(BaseModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment = serializer.save()
        
        success, result = stripe_service.create_payment_intent(
            amount=payment.amount,
            currency='usd',
            metadata={
                'payment_id': payment.id,
                'booking_id': payment.booking.id,
                'customer_id': payment.customer.id
            }
        )
        
        if success:
            payment.stripe_payment_intent_id = result.id
            payment.save()
            
            return Response({
                'payment': serializer.data,
                'client_secret': result.client_secret
            }, status=status.HTTP_201_CREATED)
        else:
            payment.delete()
            return Response({
                'error': result
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        payment = self.get_object()
        
        if not payment.stripe_payment_intent_id:
            return Response({
                'error': 'No payment intent found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        success, result = stripe_service.confirm_payment(payment.stripe_payment_intent_id)
        
        if success:
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
            
            return Response({
                'status': 'payment confirmed',
                'payment': PaymentSerializer(payment).data
            })
        else:
            payment.status = 'failed'
            payment.save()
            
            return Response({
                'error': 'Payment confirmation failed'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def transfer_to_provider(self, request, pk=None):
        payment = self.get_object()
        
        if payment.status != 'completed':
            return Response({
                'error': 'Payment not completed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        provider_stripe_account = request.data.get('provider_stripe_account')
        if not provider_stripe_account:
            return Response({
                'error': 'Provider Stripe account required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        platform_fee = payment.amount * 0.10
        transfer_amount = payment.amount - platform_fee
        
        success, result = stripe_service.transfer_to_account(
            amount=transfer_amount,
            destination_account=provider_stripe_account,
            metadata={
                'payment_id': payment.id,
                'provider_id': payment.provider.id
            }
        )
        
        if success:
            payment.stripe_transfer_id = result.id
            payment.save()
            
            return Response({
                'status': 'transfer completed',
                'transfer_amount': transfer_amount,
                'platform_fee': platform_fee
            })
        else:
            return Response({
                'error': result
            }, status=status.HTTP_400_BAD_REQUEST)
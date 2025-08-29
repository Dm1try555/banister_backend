from core.base.common_imports import *
from .models import Payment
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer, PaymentUpdateSerializer,
    PaymentConfirmSerializer, PaymentTransferSerializer
)
from core.stripe.service import stripe_service
from .permissions import PaymentPermissions
import logging

logger = logging.getLogger(__name__)


class PaymentListCreateView(OptimizedListCreateView, PaymentPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.select_related('customer', 'provider', 'booking', 'booking__service').order_by('-created_at')

    def get_serializer_class(self):
        return PaymentCreateSerializer if self.request.method == 'POST' else PaymentSerializer

    @swagger_list_create(
        description="Create new payment",
        response_schema=PAYMENT_CREATE_RESPONSE_SCHEMA,
        tags=["Payments"]
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        payment = serializer.save()
        payment.customer = self.request.user
        payment.provider = payment.booking.service.provider
        
        # Create Stripe Payment Intent
        success, result = stripe_service.create_payment_intent(
            amount=payment.amount,
            currency='usd',
            metadata={
                'payment_id': payment.id,
                'booking_id': payment.booking.id,
                'customer_id': payment.customer.id,
                'provider_id': payment.provider.id
            }
        )
        
        if success:
            payment.stripe_payment_intent_id = result.id
            payment.save()
        else:
            logger.error(f"Failed to create Stripe payment intent: {result}")
        
        payment.save()


class PaymentDetailView(OptimizedRetrieveUpdateView, PaymentPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.select_related('customer', 'provider', 'booking', 'booking__service').order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PaymentUpdateSerializer
        return PaymentSerializer

    @swagger_retrieve_update(
        description="Retrieve or update payment",
        response_schema=PAYMENT_RESPONSE_SCHEMA,
        tags=["Payments"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PaymentConfirmView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema_simple(
        operation_description="Confirm payment with Stripe",
        request_body=PaymentConfirmSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA
        },
        tags=["Payments"]
    )
    @transaction.atomic
    def post(self, request):
        serializer = PaymentConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_intent_id = serializer.validated_data['payment_intent_id']
        
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent_id,
                customer=request.user
            )
            
            # Confirm payment with Stripe
            success, result = stripe_service.confirm_payment(payment_intent_id)
            
            if success and result.status == 'succeeded':
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Payment confirmed successfully',
                    'payment_id': payment.id
                })
            else:
                payment.status = 'failed'
                payment.save()
                
                return Response({
                    'status': 'failed',
                    'message': 'Payment confirmation failed',
                    'payment_id': payment.id
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Payment.DoesNotExist:
            ErrorCode.USER_NOT_FOUND.raise_error()


class PaymentTransferView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema_simple(
        operation_description="Transfer payment to provider",
        request_body=PaymentTransferSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'transfer_id': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA
        },
        tags=["Payments"]
    )
    @transaction.atomic
    def post(self, request):
        serializer = PaymentTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_id = serializer.validated_data['payment_id']
        provider_stripe_account = serializer.validated_data['provider_stripe_account']
        
        try:
            payment = Payment.objects.get(
                id=payment_id,
                status='completed'
            )
            
            # Transfer to provider's Stripe account
            success, result = stripe_service.transfer_to_account(
                amount=payment.amount,
                destination_account=provider_stripe_account,
                currency='usd'
            )
            
            if success:
                payment.stripe_transfer_id = result.id
                payment.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Transfer completed successfully',
                    'transfer_id': result.id
                })
            else:
                return Response({
                    'status': 'failed',
                    'message': f'Transfer failed: {result}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Payment.DoesNotExist:
            ErrorCode.USER_NOT_FOUND.raise_error()


class PaymentClientSecretView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema_simple(
        operation_description="Get Stripe client secret for payment",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['payment_id']
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'client_secret': openapi.Schema(type=openapi.TYPE_STRING),
                    'payment_intent_id': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA
        },
        tags=["Payments"]
    )
    def post(self, request):
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        
        try:
            payment = Payment.objects.get(
                id=payment_id,
                customer=request.user
            )
            
            if not payment.stripe_payment_intent_id:
                ErrorCode.INVALID_DATA.raise_error()
            
            # Retrieve payment intent from Stripe
            success, result = stripe_service.get_payment_intent(payment.stripe_payment_intent_id)
            
            if success:
                return Response({
                    'client_secret': result.client_secret,
                    'payment_intent_id': payment.stripe_payment_intent_id
                })
            else:
                ErrorCode.STRIPE_SERVICE_ERROR.raise_error()
                
        except Payment.DoesNotExist:
            ErrorCode.USER_NOT_FOUND.raise_error()


class StripeAccountCreateView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema_simple(
        operation_description="Create Stripe connected account for provider",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'account_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'account_link': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA
        },
        tags=["Payments"]
    )
    @transaction.atomic
    def post(self, request):
        user = request.user
        
        # Check if user already has a Stripe account
        if user.stripe_account_id:
            return Response({
                'account_id': user.stripe_account_id,
                'message': 'User already has a Stripe account'
            })
        
        # Create Stripe connected account
        success, result = stripe_service.create_connected_account(
            email=user.email,
            country='US'
        )
        
        if success:
            # Save account ID to user
            user.stripe_account_id = result.id
            user.save()
            
            # Create account link for onboarding
            refresh_url = f"{request.build_absolute_uri('/')}stripe/refresh"
            return_url = f"{request.build_absolute_uri('/')}stripe/return"
            
            link_success, link_result = stripe_service.create_account_link(
                account_id=result.id,
                refresh_url=refresh_url,
                return_url=return_url
            )
            
            if link_success:
                return Response({
                    'account_id': result.id,
                    'account_link': link_result.url
                })
            else:
                return Response({
                    'account_id': result.id,
                    'message': 'Account created but onboarding link failed'
                })
        else:
            return Response({
                'error': result
            }, status=status.HTTP_400_BAD_REQUEST)
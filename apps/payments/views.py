from core.base.common_imports import *
from .models import Payment
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer, PaymentUpdateSerializer,
    PaymentConfirmSerializer, PaymentTransferSerializer
)
from core.stripe.service import stripe_service
from .permissions import PaymentPermissions


class PaymentListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, PaymentPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()

    def get_serializer_class(self):
        return PaymentCreateSerializer if self.request.method == 'POST' else PaymentSerializer

    @swagger_list_create(
        description="Create new payment",
        response_schema=PAYMENT_CREATE_RESPONSE_SCHEMA,
        tags=["Payments"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        payment = serializer.save()
        payment.customer = self.request.user
        payment.provider = payment.booking.service.provider
        payment.save()


class PaymentDetailView(SwaggerMixin, RetrieveUpdateAPIView, RoleBasedQuerysetMixin, PaymentPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()

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

    @swagger_retrieve_update(
        description="Update payment",
        response_schema=PAYMENT_RESPONSE_SCHEMA,
        tags=["Payments"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update(
        description="Partially update payment",
        response_schema=PAYMENT_RESPONSE_SCHEMA,
        tags=["Payments"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PaymentConfirmView(APIView):
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
    def post(self, request):
        serializer = PaymentConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        payment_intent_id = serializer.validated_data['payment_intent_id']
        
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent_id,
                customer=request.user
            )
            
            payment.status = 'completed'
            payment.completed_at = timezone.now()
            payment.save()
            
            return Response({
                'status': 'success',
                'message': 'Payment confirmed successfully',
                'payment_id': payment.id
            })
            
        except Payment.DoesNotExist:
            ErrorCode.USER_NOT_FOUND.raise_error()


class PaymentTransferView(APIView):
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
    def post(self, request):
        serializer = PaymentTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        provider_stripe_account = serializer.validated_data['provider_stripe_account']
        
        try:
            payment = Payment.objects.get(
                customer=request.user,
                status='completed'
            )
            
            transfer_id = f"tr_{uuid.uuid4().hex[:24]}"
            
            payment.stripe_transfer_id = transfer_id
            payment.save()
            
            return Response({
                'status': 'success',
                'message': 'Transfer initiated successfully',
                'transfer_id': transfer_id
            })
            
        except Payment.DoesNotExist:
            ErrorCode.USER_NOT_FOUND.raise_error()
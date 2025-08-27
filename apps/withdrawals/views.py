from core.base.common_imports import *
from .models import Withdrawal
from .serializers import (
    WithdrawalSerializer, WithdrawalCreateSerializer, WithdrawalUpdateSerializer,
    WithdrawalApproveSerializer, WithdrawalRejectSerializer
)
from core.stripe.service import stripe_service
from .permissions import WithdrawalPermissions


class WithdrawalListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, WithdrawalPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Withdrawal.objects.all()

    def get_serializer_class(self):
        return WithdrawalCreateSerializer if self.request.method == 'POST' else WithdrawalSerializer

    @swagger_list_create(
        description="Create new withdrawal request",
        response_schema=WITHDRAWAL_RESPONSE_SCHEMA,
        tags=["Withdrawals"]
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WithdrawalDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin, WithdrawalPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Withdrawal.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return WithdrawalUpdateSerializer
        return WithdrawalSerializer




class WithdrawalApproveView(SwaggerMixin, UpdateAPIView, RoleBasedQuerysetMixin, WithdrawalPermissions):
    permission_classes = [IsAuthenticated]
    serializer_class = WithdrawalApproveSerializer
    queryset = Withdrawal.objects.all()

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Withdrawal.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Withdrawal, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Withdrawal, user)
        return self._get_admin_queryset(Withdrawal, user)

    @swagger_auto_schema_simple(
        operation_description="Approve withdrawal request",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'withdrawal_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        },
        tags=["Withdrawals"]
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        withdrawal = self.get_object()
        
        if withdrawal.status != 'pending':
            ErrorCode.INVALID_DATA.raise_error()
        
        withdrawal.status = 'approved'
        withdrawal.completed_at = timezone.now()
        withdrawal.save()
        
        return Response({
            'status': 'success',
            'message': 'Withdrawal approved successfully',
            'withdrawal_id': withdrawal.id
        })


class WithdrawalRejectView(SwaggerMixin, UpdateAPIView, RoleBasedQuerysetMixin, WithdrawalPermissions):
    permission_classes = [IsAuthenticated]
    serializer_class = WithdrawalRejectSerializer
    queryset = Withdrawal.objects.all()

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Withdrawal.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Withdrawal, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Withdrawal, user)
        return self._get_admin_queryset(Withdrawal, user)

    @swagger_auto_schema_simple(
        operation_description="Reject withdrawal request",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'withdrawal_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                }
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        },
        tags=["Withdrawals"]
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        withdrawal = self.get_object()
        serializer = self.get_serializer(withdrawal, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        if withdrawal.status != 'pending':
            ErrorCode.INVALID_DATA.raise_error()
        
        withdrawal.status = 'rejected'
        withdrawal.save()
        
        return Response({
            'status': 'success',
            'message': 'Withdrawal rejected successfully',
            'withdrawal_id': withdrawal.id
        })
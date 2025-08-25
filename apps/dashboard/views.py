from core.base.common_imports import *
from .models import CustomerDashboard, ProviderDashboard, ManagementDashboard
from .serializers import (
    CustomerDashboardSerializer, CustomerDashboardUpdateSerializer,
    ProviderDashboardSerializer, ProviderDashboardUpdateSerializer,
    ManagementDashboardSerializer, ManagementDashboardUpdateSerializer
)
from .permissions import DashboardPermissions


class CustomerDashboardView(SwaggerMixin, RetrieveUpdateAPIView, RoleBasedQuerysetMixin, DashboardPermissions):
    permission_classes = [IsAuthenticated]
    queryset = CustomerDashboard.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CustomerDashboardUpdateSerializer
        return CustomerDashboardSerializer

    @swagger_retrieve_update(
        description="Retrieve or update customer dashboard",
        response_schema=CUSTOMER_DASHBOARD_RESPONSE_SCHEMA,
        tags=["Customer Dashboard"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_retrieve_update(
        description="Update customer dashboard",
        response_schema=CUSTOMER_DASHBOARD_RESPONSE_SCHEMA,
        tags=["Customer Dashboard"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update(
        description="Partially update customer dashboard",
        response_schema=CUSTOMER_DASHBOARD_RESPONSE_SCHEMA,
        tags=["Customer Dashboard"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ProviderDashboardView(SwaggerMixin, RetrieveUpdateAPIView, RoleBasedQuerysetMixin, DashboardPermissions):
    permission_classes = [IsAuthenticated]
    queryset = ProviderDashboard.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProviderDashboardUpdateSerializer
        return ProviderDashboardSerializer

    @swagger_retrieve_update(
        description="Retrieve or update provider dashboard",
        response_schema=PROVIDER_DASHBOARD_RESPONSE_SCHEMA,
        tags=["Provider Dashboard"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_retrieve_update(
        description="Update provider dashboard",
        response_schema=PROVIDER_DASHBOARD_RESPONSE_SCHEMA,
        tags=["Provider Dashboard"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update(
        description="Partially update provider dashboard",
        response_schema=PROVIDER_DASHBOARD_RESPONSE_SCHEMA,
        tags=["Provider Dashboard"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ManagementDashboardView(SwaggerMixin, RetrieveUpdateAPIView, RoleBasedQuerysetMixin, DashboardPermissions):
    permission_classes = [IsAuthenticated]
    queryset = ManagementDashboard.objects.all()

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return ManagementDashboard.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(ManagementDashboard, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(ManagementDashboard, user)
        return self._get_admin_queryset(ManagementDashboard, user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ManagementDashboardUpdateSerializer
        return ManagementDashboardSerializer

    @swagger_retrieve_update(
        description="Retrieve or update management dashboard",
        response_schema=MANAGEMENT_DASHBOARD_RESPONSE_SCHEMA,
        tags=["Management Dashboard"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_retrieve_update(
        description="Update management dashboard",
        response_schema=MANAGEMENT_DASHBOARD_RESPONSE_SCHEMA,
        tags=["Management Dashboard"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update(
        description="Partially update management dashboard",
        response_schema=MANAGEMENT_DASHBOARD_RESPONSE_SCHEMA,
        tags=["Management Dashboard"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
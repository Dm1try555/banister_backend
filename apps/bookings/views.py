from core.base.common_imports import *
from core.base.role_base import RoleBase
from .models import Booking, Interview
from .serializers import (
    BookingSerializer, BookingCreateSerializer, BookingUpdateSerializer,
    InterviewSerializer, InterviewCreateSerializer, InterviewUpdateSerializer
)


class BookingListCreateView(SwaggerMixin, ListCreateAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Booking.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Booking, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Booking, user)
        return self._get_admin_queryset(Booking, user)

    def get_serializer_class(self):
        return BookingCreateSerializer if self.request.method == 'POST' else BookingSerializer

    @swagger_list_create(
        description="Create new booking",
        response_schema=BOOKING_RESPONSE_SCHEMA,
        tags=["Bookings"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class BookingDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Booking.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Booking, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Booking, user)
        return self._get_admin_queryset(Booking, user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookingUpdateSerializer
        return BookingSerializer

    @swagger_retrieve_update_destroy(
        description="Retrieve, update or delete booking",
        response_schema=BOOKING_RESPONSE_SCHEMA,
        tags=["Bookings"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Update booking",
        response_schema=BOOKING_RESPONSE_SCHEMA,
        tags=["Bookings"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Partially update booking",
        response_schema=BOOKING_RESPONSE_SCHEMA,
        tags=["Bookings"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete booking",
        response_schema=openapi.Response(description="Booking deleted successfully"),
        tags=["Bookings"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class InterviewListCreateView(SwaggerMixin, ListCreateAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Interview.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Interview, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Interview, user)
        return self._get_admin_queryset(Interview, user)

    def get_serializer_class(self):
        return InterviewCreateSerializer if self.request.method == 'POST' else InterviewSerializer

    @swagger_list_create(
        description="Create new interview",
        response_schema=INTERVIEW_RESPONSE_SCHEMA,
        tags=["Interviews"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class InterviewDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Interview.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Interview, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Interview, user)
        return self._get_admin_queryset(Interview, user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InterviewUpdateSerializer
        return InterviewSerializer

    @swagger_retrieve_update_destroy(
        description="Retrieve, update or delete interview",
        response_schema=INTERVIEW_RESPONSE_SCHEMA,
        tags=["Interviews"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Update interview",
        response_schema=INTERVIEW_RESPONSE_SCHEMA,
        tags=["Interviews"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Partially update interview",
        response_schema=INTERVIEW_RESPONSE_SCHEMA,
        tags=["Interviews"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete interview",
        response_schema=openapi.Response(description="Interview deleted successfully"),
        tags=["Interviews"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
from core.base.common_imports import *
from .models import Booking
from .serializers import (
    BookingSerializer, BookingCreateSerializer, BookingUpdateSerializer
)
from .permissions import BookingPermissions


class BookingListCreateView(OptimizedListCreateView, BookingPermissions):
    queryset = Booking.objects.select_related('customer', 'service', 'provider').order_by('-id')

    def get_serializer_class(self):
        return BookingCreateSerializer if self.request.method == 'POST' else BookingSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        self.check_permission('create_booking')
        serializer.save(customer=self.request.user)


class BookingDetailView(OptimizedRetrieveUpdateDestroyView, BookingPermissions):
    queryset = Booking.objects.select_related('customer', 'service', 'provider').order_by('-id')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookingUpdateSerializer
        return BookingSerializer



    @transaction.atomic
    def put(self, request, *args, **kwargs):
        self.check_permission('edit_booking')
        return super().put(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        self.check_permission('edit_booking')
        return super().patch(request, *args, **kwargs)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        self.check_permission('delete_booking')
        return super().delete(request, *args, **kwargs)



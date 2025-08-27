from core.base.common_imports import *
from .models import Booking, Interview
from .serializers import (
    BookingSerializer, BookingCreateSerializer, BookingUpdateSerializer,
    InterviewSerializer, InterviewCreateSerializer, InterviewUpdateSerializer
)
from .permissions import BookingPermissions, InterviewPermissions


class BookingListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, BookingPermissions):
    permission_classes = [IsAuthenticated]  # Только зарегистрированные могут просматривать
    queryset = Booking.objects.all()

    def get_serializer_class(self):
        return BookingCreateSerializer if self.request.method == 'POST' else BookingSerializer

    def perform_create(self, serializer):
        self.check_permission('create_booking')
        serializer.save(customer=self.request.user)


class BookingDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin, BookingPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BookingUpdateSerializer
        return BookingSerializer



    def put(self, request, *args, **kwargs):
        self.check_permission('edit_booking')
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.check_permission('edit_booking')
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.check_permission('delete_booking')
        return super().delete(request, *args, **kwargs)


class InterviewListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, InterviewPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Interview.objects.all()

    def get_serializer_class(self):
        return InterviewCreateSerializer if self.request.method == 'POST' else InterviewSerializer

    def perform_create(self, serializer):
        # Проверяем разрешение на создание
        self.check_permission('create_interview')
        serializer.save(customer=self.request.user)


class InterviewDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin, InterviewPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Interview.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InterviewUpdateSerializer
        return InterviewSerializer



    def put(self, request, *args, **kwargs):
        self.check_permission('edit_interview')
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        self.check_permission('edit_interview')
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.check_permission('delete_interview')
        return super().delete(request, *args, **kwargs)
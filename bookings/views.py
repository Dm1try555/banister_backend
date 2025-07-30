from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    PermissionError, NotFoundError, BookingNotFoundError,
    ValidationError, ConflictError
)
from error_handling.utils import ErrorResponseMixin, format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class BookingListCreateView(BaseAPIView, generics.ListCreateAPIView):
    """List and create bookings"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # For swagger schema generation or if no user.role — return empty queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Booking.objects.none()
        # customer sees their orders, provider sees orders for their services
        if self.request.user.role == 'customer':
            return Booking.objects.filter(customer=self.request.user)
        elif self.request.user.role == 'provider':
            return Booking.objects.filter(provider=self.request.user)
        return Booking.objects.none()

    @transaction.atomic
    def perform_create(self, serializer):
        # Check access rights
        if self.request.user.role != 'customer':
            raise PermissionError('Only customers can create bookings')
        
        # Check time availability
        service = serializer.validated_data.get('service')
        booking_date = serializer.validated_data.get('booking_date')
        booking_time = serializer.validated_data.get('booking_time')
        
        # Check for time conflict
        conflicting_booking = Booking.objects.filter(
            service=service,
            booking_date=booking_date,
            booking_time=booking_time,
            status__in=['confirmed', 'pending']
        ).first()
        
        if conflicting_booking:
            raise ConflictError('Selected time is already booked')
        
        booking = serializer.save(customer=self.request.user)

    @swagger_auto_schema(
        operation_description="Get list of all user bookings (customer sees their own, provider sees their own)",
        responses={
            200: openapi.Response('Booking list', BookingSerializer(many=True)),
            403: 'No access rights',
        },
        tags=['Bookings']
    )
    def list(self, request, *args, **kwargs):
        """
        Get booking list
        """
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Booking list retrieved successfully'
            )
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_LIST_ERROR',
                error_message=f'Error retrieving booking list: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Create new booking (customers only)",
        request_body=BookingSerializer,
        responses={
            201: openapi.Response('Booking created', BookingSerializer),
            400: 'Validation error',
            403: 'No access rights',
            409: 'Time conflict',
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create new booking
        """
        try:
            # Check access rights
            if self.request.user.role != 'customer':
                raise PermissionError('Only customers can create bookings')
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Check time availability
            service = serializer.validated_data.get('service')
            booking_date = serializer.validated_data.get('booking_date')
            booking_time = serializer.validated_data.get('booking_time')
            
            # Check for time conflict
            conflicting_booking = Booking.objects.filter(
                service=service,
                booking_date=booking_date,
                booking_time=booking_time,
                status__in=['confirmed', 'pending']
            ).first()
            
            if conflicting_booking:
                raise ConflictError('Selected time is already booked')
            
            booking = serializer.save(customer=self.request.user)
            
            return self.success_response(
                data=serializer.data,
                message='Booking created successfully'
            )
            
        except PermissionError:
            raise
        except ConflictError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_CREATE_ERROR',
                error_message=f'Error creating booking: {str(e)}',
                status_code=500
            )

class BookingDetailView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    """Detailed booking information"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # For swagger schema generation or if no user.role — return empty queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Booking.objects.none()
        # customer sees their orders, provider sees orders for their services
        if self.request.user.role == 'customer':
            return Booking.objects.filter(customer=self.request.user)
        elif self.request.user.role == 'provider':
            return Booking.objects.filter(provider=self.request.user)
        return Booking.objects.none()

    @swagger_auto_schema(
        operation_description="Get detailed booking information by ID (owner only)",
        responses={
            200: openapi.Response('Booking information', BookingSerializer),
            404: 'Booking not found',
        },
        tags=['Bookings']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Get detailed booking information
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Booking information retrieved successfully'
            )
            
        except Booking.DoesNotExist:
            raise BookingNotFoundError('Booking not found')
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_RETRIEVE_ERROR',
                error_message=f'Error retrieving booking information: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Update booking data (owner only)",
        request_body=BookingSerializer,
        responses={
            200: openapi.Response('Booking updated', BookingSerializer),
            400: 'Validation error',
            403: 'No permissions',
            404: 'Booking not found',
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update booking
        """
        try:
            instance = self.get_object()
            
            # Check update permissions
            if self.request.user.role == 'customer' and instance.customer != self.request.user:
                raise PermissionError('No permissions to update this booking')
            
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Check booking status
            if instance.status in ['cancelled', 'completed']:
                raise ValidationError('Cannot modify completed or cancelled booking')
            
            booking = serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message='Booking updated successfully'
            )
            
        except Booking.DoesNotExist:
            raise BookingNotFoundError('Booking not found')
        except PermissionError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_UPDATE_ERROR',
                error_message=f'Error updating booking: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Delete booking (owner only)",
        responses={
            200: 'Booking deleted',
            403: 'No permissions',
            404: 'Booking not found',
        },
        tags=['Bookings']
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete booking
        """
        try:
            instance = self.get_object()
            
            # Check delete permissions
            if self.request.user.role == 'customer' and instance.customer != self.request.user:
                raise PermissionError('No permissions to delete this booking')
            
            instance.delete()
            
            return self.success_response(
                message='Booking deleted successfully'
            )
            
        except Booking.DoesNotExist:
            raise BookingNotFoundError('Booking not found')
        except PermissionError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_DELETE_ERROR',
                error_message=f'Error deleting booking: {str(e)}',
                status_code=500
            )

class BookingStatusUpdateView(BaseAPIView):
    """Update booking status (for providers)"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change booking status (providers only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='New status'),
            },
            required=['status'],
        ),
        responses={
            200: 'Status updated',
            400: 'Request error',
            403: 'No permissions',
            404: 'Booking not found',
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def post(self, request, booking_id):
        """
        Update booking status
        """
        try:
            # Check user role
            if self.request.user.role != 'provider':
                raise PermissionError('Only providers can update booking status')
            
            # Get booking
            try:
                booking = Booking.objects.get(id=booking_id, provider=self.request.user)
            except Booking.DoesNotExist:
                raise BookingNotFoundError('Booking not found')
            
            new_status = request.data.get('status')
            if not new_status:
                return self.error_response(
                    error_number='MISSING_STATUS',
                    error_message='Status not specified',
                    status_code=400
                )
            
            # Validate status
            valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
            if new_status not in valid_statuses:
                return self.error_response(
                    error_number='INVALID_STATUS',
                    error_message=f'Invalid status. Allowed values: {", ".join(valid_statuses)}',
                    status_code=400
                )
            
            booking.status = new_status
            booking.save()
            
            return self.success_response(
                data={'status': new_status},
                message='Booking status updated successfully'
            )
            
        except PermissionError:
            raise
        except BookingNotFoundError:
            raise
        except Exception as e:
            return self.error_response(
                error_number='STATUS_UPDATE_ERROR',
                error_message=f'Error updating status: {str(e)}',
                status_code=500
            )
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Booking
from .serializers import BookingSerializer

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    CustomPermissionError, NotFoundError, BookingNotFoundError,
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

    @swagger_auto_schema(
        operation_description="Get list of all user bookings (customer sees their own, provider sees their own)",
        responses={
            200: openapi.Response('Booking list', BookingSerializer(many=True)),
            500: 'Server error'
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
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['service', 'date'],
            properties={
                'service': openapi.Schema(type=openapi.TYPE_INTEGER, description='Service ID'),
                'date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Booking date and time'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Booking status (optional)', default='pending')
            },
            example={
                'service': 1,
                'date': '2024-01-15T14:00:00Z',
                'status': 'pending'
            }
        ),
        responses={
            201: openapi.Response('Booking created', BookingSerializer),
            400: 'Validation error',
            401: 'Authentication required',
            403: 'Only customers can create bookings',
            409: 'Time conflict',
            500: 'Server error'
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create new booking
        """
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            # Check access rights
            if request.user.role != 'customer':
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='Only customers can create bookings',
                    status_code=403
                )
            
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Check time availability
            service = serializer.validated_data.get('service')
            booking_date = serializer.validated_data.get('date')
            
            # Check for time conflict
            conflicting_booking = Booking.objects.filter(
                service=service,
                date=booking_date,
                status__in=['confirmed', 'pending']
            ).first()
            
            if conflicting_booking:
                return self.error_response(
                    error_number='TIME_CONFLICT',
                    error_message='Selected time is already booked',
                    status_code=409
                )
            
            # Set customer and provider (provider comes from service)
            booking = serializer.save(
                customer=request.user,
                provider=service.provider
            )
            
            return self.success_response(
                data=serializer.data,
                message='Booking created successfully'
            )
            
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
            401: 'Authentication required',
            404: 'Booking not found',
            500: 'Server error'
        },
        tags=['Bookings']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Get detailed booking information
        """
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Booking information retrieved successfully'
            )
            
        except Booking.DoesNotExist:
            return self.error_response(
                error_number='BOOKING_NOT_FOUND',
                error_message='Booking not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_RETRIEVE_ERROR',
                error_message=f'Error retrieving booking information: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Update booking data (owner only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'service': openapi.Schema(type=openapi.TYPE_INTEGER, description='Service ID'),
                'date': openapi.Schema(type=openapi.TYPE_STRING, format='date-time', description='Booking date and time'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Booking status')
            },
            example={
                'date': '2024-01-16T15:00:00Z',
                'status': 'confirmed'
            }
        ),
        responses={
            200: openapi.Response('Booking updated', BookingSerializer),
            400: 'Validation error',
            401: 'Authentication required',
            403: 'No permissions to update this booking',
            404: 'Booking not found',
            500: 'Server error'
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        Update booking
        """
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            instance = self.get_object()
            
            # Check update permissions
            if request.user.role == 'customer' and instance.customer != request.user:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='No permissions to update this booking',
                    status_code=403
                )
            
            serializer = self.get_serializer(instance, data=request.data, partial=False)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Check booking status
            if instance.status in ['cancelled', 'completed']:
                return self.error_response(
                    error_number='INVALID_STATUS',
                    error_message='Cannot modify completed or cancelled booking',
                    status_code=400
                )
            
            booking = serializer.save()
            
            return self.success_response(
                data=serializer.data,
                message='Booking updated successfully'
            )
            
        except Booking.DoesNotExist:
            return self.error_response(
                error_number='BOOKING_NOT_FOUND',
                error_message='Booking not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_UPDATE_ERROR',
                error_message=f'Error updating booking: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Delete booking (owner only)",
        responses={
            200: 'Booking deleted successfully',
            401: 'Authentication required',
            403: 'No permissions to delete this booking',
            404: 'Booking not found',
            500: 'Server error'
        },
        tags=['Bookings']
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete booking
        """
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            instance = self.get_object()
            
            # Check delete permissions
            if request.user.role == 'customer' and instance.customer != request.user:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='No permissions to delete this booking',
                    status_code=403
                )
            
            instance.delete()
            
            return self.success_response(
                message='Booking deleted successfully'
            )
            
        except Booking.DoesNotExist:
            return self.error_response(
                error_number='BOOKING_NOT_FOUND',
                error_message='Booking not found',
                status_code=404
            )
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
            example={
                'status': 'confirmed'
            }
        ),
        responses={
            200: 'Status updated successfully',
            400: 'Invalid status or missing status',
            401: 'Authentication required',
            403: 'Only providers can update booking status',
            404: 'Booking not found',
            500: 'Server error'
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def post(self, request, booking_id):
        """
        Update booking status
        """
        try:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            # Check user role
            if request.user.role != 'provider':
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='Only providers can update booking status',
                    status_code=403
                )
            
            # Get booking
            try:
                booking = Booking.objects.get(id=booking_id, provider=request.user)
            except Booking.DoesNotExist:
                return self.error_response(
                    error_number='BOOKING_NOT_FOUND',
                    error_message='Booking not found',
                    status_code=404
                )
            
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
            
        except Exception as e:
            return self.error_response(
                error_number='STATUS_UPDATE_ERROR',
                error_message=f'Error updating status: {str(e)}',
                status_code=500
            )
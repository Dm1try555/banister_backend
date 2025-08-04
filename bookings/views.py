from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Booking
from .serializers import (
    BookingSerializer, BookingCreateSerializer, BookingUpdateSerializer, 
    BookingStatusUpdateSerializer, ServiceSearchSerializer, 
    ProviderSearchRequestSerializer
)
from services.models import Service
from .google_calendar_service import google_calendar_service

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

class IsCustomerOrReadOnly:
    """Permissions for customers or read-only"""
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'customer'

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.customer == request.user

class SendMeetingInvitationView(BaseAPIView):
    """Отправка приглашений на встречу через Google Calendar"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Отправить приглашения на встречу пользователям с подтвержденной почтой",
        responses={
            200: openapi.Response('Приглашения отправлены', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'calendar_created': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'calendar_event_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'emails_sent': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'total_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            403: 'Нет прав для отправки приглашений',
            404: 'Бронирование не найдено',
            500: 'Ошибка сервера'
        },
        tags=['Bookings']
    )
    @transaction.atomic
    def post(self, request, booking_id):
        """Отправить приглашения на встречу"""
        try:
            # Проверка аутентификации
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Требуется аутентификация',
                    status_code=401
                )
            
            # Получение бронирования
            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return self.error_response(
                    error_number='BOOKING_NOT_FOUND',
                    error_message='Бронирование не найдено',
                    status_code=404
                )
            
            # Проверка прав доступа - только клиент или провайдер могут отправлять приглашения
            if request.user not in [booking.customer, booking.provider]:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='Нет прав для отправки приглашений',
                    status_code=403
                )
            
            # Проверка статуса бронирования
            if booking.status not in ['confirmed', 'pending']:
                return self.error_response(
                    error_number='INVALID_STATUS',
                    error_message='Можно отправлять приглашения только для подтвержденных или ожидающих бронирований',
                    status_code=400
                )
            
            # Проверка времени встречи
            if not booking.scheduled_datetime:
                return self.error_response(
                    error_number='NO_SCHEDULED_TIME',
                    error_message='Время встречи не назначено',
                    status_code=400
                )
            
            # Отправка приглашений
            result = google_calendar_service.send_meeting_invitations(booking)
            
            # Обновление информации о бронировании
            booking.calendar_invitations_sent = True
            booking.calendar_sent_at = timezone.now()
            if result['calendar_event_id']:
                booking.google_calendar_event_id = result['calendar_event_id']
            booking.save()
            
            return self.success_response(
                data=result,
                message=f'Приглашения отправлены. Email отправлено: {result["emails_sent"]}/{result["total_users"]}'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='INVITATION_SEND_ERROR',
                error_message=f'Ошибка отправки приглашений: {str(e)}',
                status_code=500
            )

class AdminSendMeetingInvitationView(BaseAPIView):
    """Отправка приглашений на встречу администратором"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Отправить приглашения на встречу (только админ)",
        responses={
            200: openapi.Response('Приглашения отправлены', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'calendar_created': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'calendar_event_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'emails_sent': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'total_users': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Ошибка валидации',
            401: 'Требуется аутентификация',
            403: 'Только администраторы могут отправлять приглашения',
            404: 'Бронирование не найдено',
            500: 'Ошибка сервера'
        },
        tags=['Admin']
    )
    @transaction.atomic
    def post(self, request, booking_id):
        """Отправить приглашения на встречу (админ)"""
        try:
            # Проверка аутентификации
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Требуется аутентификация',
                    status_code=401
                )
            
            # Проверка прав администратора
            if not request.user.is_staff:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='Только администраторы могут отправлять приглашения',
                    status_code=403
                )
            
            # Получение бронирования
            try:
                booking = Booking.objects.get(id=booking_id)
            except Booking.DoesNotExist:
                return self.error_response(
                    error_number='BOOKING_NOT_FOUND',
                    error_message='Бронирование не найдено',
                    status_code=404
                )
            
            # Проверка времени встречи
            if not booking.scheduled_datetime:
                return self.error_response(
                    error_number='NO_SCHEDULED_TIME',
                    error_message='Время встречи не назначено',
                    status_code=400
                )
            
            # Отправка приглашений
            result = google_calendar_service.send_meeting_invitations(booking)
            
            # Обновление информации о бронировании
            booking.calendar_invitations_sent = True
            booking.calendar_sent_at = timezone.now()
            if result['calendar_event_id']:
                booking.google_calendar_event_id = result['calendar_event_id']
            booking.save()
            
            return self.success_response(
                data=result,
                message=f'Приглашения отправлены администратором. Email отправлено: {result["emails_sent"]}/{result["total_users"]}'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='ADMIN_INVITATION_SEND_ERROR',
                error_message=f'Ошибка отправки приглашений администратором: {str(e)}',
                status_code=500
            )

class ProviderSearchView(BaseAPIView):
    """Search for available providers based on criteria"""
    permission_classes = []  # Remove permission class
    
    # Use GET method for search with query parameters
    http_method_names = ['get']
    
    @swagger_auto_schema(
        operation_description="Search for available providers based on criteria",
        manual_parameters=[
            openapi.Parameter(
                'service_type', 
                openapi.IN_QUERY, 
                description="Type of service (e.g., 'maid', 'gardener', 'chef')",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'location', 
                openapi.IN_QUERY, 
                description="Service location/address",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'preferred_date', 
                openapi.IN_QUERY, 
                description="Preferred service date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'preferred_time', 
                openapi.IN_QUERY, 
                description="Preferred service time (HH:MM)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'frequency', 
                openapi.IN_QUERY, 
                description="Service frequency",
                type=openapi.TYPE_STRING,
                enum=['one_time', 'weekly', 'biweekly', 'monthly'],
                default='one_time'
            ),
            openapi.Parameter(
                'max_price', 
                openapi.IN_QUERY, 
                description="Maximum price willing to pay",
                type=openapi.TYPE_NUMBER,
                required=False
            ),
        ],
        responses={
            200: openapi.Response('Providers found', ServiceSearchSerializer),
            400: 'Validation error',
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Bookings']
    )
    def get(self, request):
        """Search for available providers"""
        try:
            # Check authentication
            if not request.user.is_authenticated:
                return self.error_response(
                    error_number='AUTHENTICATION_REQUIRED',
                    error_message='Authentication required',
                    status_code=401
                )
            
            # Get query parameters (all optional now)
            service_type = request.query_params.get('service_type')
            location = request.query_params.get('location')
            preferred_date_str = request.query_params.get('preferred_date')
            preferred_time_str = request.query_params.get('preferred_time')
            frequency = request.query_params.get('frequency', 'one_time')
            max_price = request.query_params.get('max_price')
            
            # Start with all services
            services = Service.objects.all()
            
            # Filter by service type if provided
            if service_type:
                services = services.filter(
                    Q(title__icontains=service_type) |
                    Q(description__icontains=service_type)
                )
            
            # Filter by price if specified
            if max_price:
                try:
                    max_price_decimal = float(max_price)
                    services = services.filter(price__lte=max_price_decimal)
                except ValueError:
                    return self.error_response(
                        error_number='INVALID_PRICE',
                        error_message='Invalid max_price format',
                        status_code=400
                    )
            
            # Filter by availability if date and time are provided
            available_services = []
            for service in services:
                # If date and time are provided, check for conflicts
                if preferred_date_str and preferred_time_str:
                    try:
                        preferred_date = datetime.strptime(preferred_date_str, '%Y-%m-%d').date()
                        preferred_time = datetime.strptime(preferred_time_str, '%H:%M').time()
                        
                        # Check if provider has conflicting bookings
                        conflicting_bookings = Booking.objects.filter(
                            service=service,
                            scheduled_datetime__date=preferred_date,
                            status__in=['pending', 'confirmed']
                        )
                        
                        if not conflicting_bookings.exists():
                            available_services.append(service)
                    except ValueError:
                        return self.error_response(
                            error_number='INVALID_DATE_FORMAT',
                            error_message='Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time',
                            status_code=400
                        )
                else:
                    # If no date/time provided, include all services
                    available_services.append(service)
            
            # Serialize results
            result_serializer = ServiceSearchSerializer(available_services, many=True)
            
            return self.success_response(
                data=result_serializer.data,
                message=f'Found {len(available_services)} available providers'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='PROVIDER_SEARCH_ERROR',
                error_message=f'Error searching for providers: {str(e)}',
                status_code=500
            )

class BookingListView(BaseAPIView):
    """List user bookings"""
    permission_classes = []  # Remove permission class
    
    # Only allow GET method
    http_method_names = ['get']
    
    @swagger_auto_schema(
        operation_description="Get list of user bookings",
        responses={
            200: openapi.Response('Bookings retrieved', BookingSerializer),
            401: 'Authentication required',
            500: 'Server error'
        },
        tags=['Bookings']
    )
    def get(self, request):
        """
        Get booking list
        """
        try:
            queryset = self.get_queryset()
            serializer = BookingSerializer(queryset, many=True)
            
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

class BookingCreateView(BaseAPIView):
    """Create new booking"""
    permission_classes = []  # Remove permission class
    
    # Only allow POST method
    http_method_names = ['post']
    
    @swagger_auto_schema(
        operation_description="Create new booking (customers only)",
        request_body=BookingCreateSerializer,
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
    def post(self, request):
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
            
            # Check access rights - only customers can create bookings
            if request.user.role != 'customer':
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='Only customers can create bookings',
                    status_code=403
                )
            
            serializer = BookingCreateSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            # Get service and validate
            service = serializer.validated_data.get('service')
            if not service:
                return self.error_response(
                    error_number='SERVICE_NOT_FOUND',
                    error_message='Service not found',
                    status_code=404
                )
            
            # Combine preferred date and time
            preferred_date = serializer.validated_data.get('preferred_date')
            preferred_time = serializer.validated_data.get('preferred_time')
            scheduled_datetime = datetime.combine(preferred_date, preferred_time)
            
            # Check for time conflicts
            conflicting_booking = Booking.objects.filter(
                service=service,
                scheduled_datetime=scheduled_datetime,
                status__in=['confirmed', 'pending']
            ).first()
            
            if conflicting_booking:
                return self.error_response(
                    error_number='TIME_CONFLICT',
                    error_message='Selected time is already booked',
                    status_code=409
                )
            
            # Create booking with all details
            booking_data = serializer.validated_data.copy()
            booking_data['scheduled_datetime'] = scheduled_datetime
            booking_data['customer'] = request.user
            booking_data['provider'] = service.provider
            
            booking = Booking.objects.create(**booking_data)
            
            # Serialize response
            response_serializer = BookingSerializer(booking)
            
            return self.success_response(
                data=response_serializer.data,
                message='Booking created successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_CREATE_ERROR',
                error_message=f'Error creating booking: {str(e)}',
                status_code=500
            )

class BookingDetailView(BaseAPIView):
    """Get and update booking details"""
    permission_classes = []  # Remove permission class
    
    # Only allow GET and PUT methods
    http_method_names = ['get', 'put']
    
    @swagger_auto_schema(
        operation_description="Get detailed booking information",
        responses={
            200: openapi.Response('Booking details', BookingSerializer),
            401: 'Authentication required',
            404: 'Booking not found',
            500: 'Server error'
        },
        tags=['Bookings']
    )
    def get(self, request, pk):
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
            
            try:
                instance = self.get_queryset().get(pk=pk)
            except Booking.DoesNotExist:
                return self.error_response(
                    error_number='BOOKING_NOT_FOUND',
                    error_message='Booking not found',
                    status_code=404
                )
            
            serializer = BookingSerializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Booking information retrieved successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_RETRIEVE_ERROR',
                error_message=f'Error retrieving booking information: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Update booking details (customers only)",
        request_body=BookingUpdateSerializer,
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
    def put(self, request, pk):
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
            
            try:
                instance = self.get_queryset().get(pk=pk)
            except Booking.DoesNotExist:
                return self.error_response(
                    error_number='BOOKING_NOT_FOUND',
                    error_message='Booking not found',
                    status_code=404
                )
            
            # Check update permissions - only customers can update their own bookings
            if request.user.role != 'customer' or instance.customer != request.user:
                return self.error_response(
                    error_number='PERMISSION_DENIED',
                    error_message='No permissions to update this booking',
                    status_code=403
                )
            
            serializer = BookingUpdateSerializer(instance, data=request.data, partial=False)
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
            
            # Update scheduled datetime if date/time changed
            if 'preferred_date' in serializer.validated_data or 'preferred_time' in serializer.validated_data:
                preferred_date = serializer.validated_data.get('preferred_date', instance.preferred_date)
                preferred_time = serializer.validated_data.get('preferred_time', instance.preferred_time)
                scheduled_datetime = datetime.combine(preferred_date, preferred_time)
                serializer.validated_data['scheduled_datetime'] = scheduled_datetime
            
            booking = serializer.save()
            
            response_serializer = BookingSerializer(booking)
            
            return self.success_response(
                data=response_serializer.data,
                message='Booking updated successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='BOOKING_UPDATE_ERROR',
                error_message=f'Error updating booking: {str(e)}',
                status_code=500
            )

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

class BookingStatusUpdateView(BaseAPIView):
    """Update booking status (for providers)"""
    permission_classes = []  # Remove permission class
    
    # Only allow POST method
    http_method_names = ['post']
    
    @swagger_auto_schema(
        operation_description="Update booking status (providers only)",
        request_body=BookingStatusUpdateSerializer,
        responses={
            200: openapi.Response('Status updated', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            400: 'Validation error',
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
            
            # Check user role - only providers can update status
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
            
            serializer = BookingStatusUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            new_status = serializer.validated_data['status']
            
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
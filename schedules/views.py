from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Schedule
from .serializers import ScheduleSerializer

# Import error handling system
from error_handling.views import BaseAPIView
from error_handling.exceptions import (
    PermissionError, ValidationError, NotFoundError, ConflictError
)
from error_handling.utils import format_validation_errors

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction

class ScheduleListCreateView(BaseAPIView, generics.ListCreateAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # For swagger schema generation or if no user.role — return empty queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Schedule.objects.none()
        return Schedule.objects.filter(provider=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        # Check user role
        if self.request.user.role != 'provider':
            raise PermissionError('Only service providers can create schedules')
        
        # Check for time conflict
        start_time = serializer.validated_data.get('start_time')
        end_time = serializer.validated_data.get('end_time')
        date = serializer.validated_data.get('date')
        
        conflicting_schedule = Schedule.objects.filter(
            provider=self.request.user,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).first()
        
        if conflicting_schedule:
            raise ConflictError('Selected time is already booked in the schedule')
        
        serializer.save(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Get provider's schedule (all slots)",
        responses={
            200: openapi.Response('Schedule list', ScheduleSerializer(many=True)),
        },
        tags=['Schedule']
    )
    def list(self, request, *args, **kwargs):
        try:
            # Filter schedule by provider
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            
            return self.success_response(
                data=serializer.data,
                message='Schedule retrieved successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_LIST_ERROR',
                error_message=f'Error retrieving schedule: {str(e)}',
                status_code=500
            )

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="Create new schedule slot (providers only)",
        request_body=ScheduleSerializer,
        responses={
            201: openapi.Response('Schedule created', ScheduleSerializer),
            400: 'Validation error',
            403: 'No permissions',
            409: 'Time conflict',
        },
        tags=['Schedule']
    )
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_create(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Schedule created successfully'
            )
            
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_CREATE_ERROR',
                error_message=f'Error creating schedule: {str(e)}',
                status_code=500
            )

class ScheduleDetailView(BaseAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # For swagger schema generation or if no user.role — return empty queryset
        if getattr(self, 'swagger_fake_view', False) or not hasattr(self.request.user, 'role'):
            return Schedule.objects.none()
        return Schedule.objects.filter(provider=self.request.user)

    @swagger_auto_schema(
        operation_description="Get detailed information about a schedule slot by ID",
        responses={
            200: openapi.Response('Schedule information', ScheduleSerializer),
            404: 'Schedule not found',
        },
        tags=['Schedule']
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Check access rights
            if instance.provider != self.request.user:
                raise PermissionError('No permissions to view this schedule')
            
            serializer = self.get_serializer(instance)
            
            return self.success_response(
                data=serializer.data,
                message='Schedule information retrieved successfully'
            )
            
        except Schedule.DoesNotExist:
            return self.error_response(
                error_number='SCHEDULE_NOT_FOUND',
                error_message='Schedule not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_RETRIEVE_ERROR',
                error_message=f'Error retrieving schedule information: {str(e)}',
                status_code=500
            )

    @transaction.atomic
    @swagger_auto_schema(
        operation_description="Update schedule slot (owner only)",
        request_body=ScheduleSerializer,
        responses={
            200: openapi.Response('Schedule updated', ScheduleSerializer),
            400: 'Validation error',
            403: 'No permissions',
            404: 'Schedule not found',
            409: 'Time conflict',
        },
        tags=['Schedule']
    )
    def update(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
            if not serializer.is_valid():
                field_errors = format_validation_errors(serializer.errors)
                return self.validation_error_response(field_errors)
            
            self.perform_update(serializer)
            
            return self.success_response(
                data=serializer.data,
                message='Schedule updated successfully'
            )
            
        except Schedule.DoesNotExist:
            return self.error_response(
                error_number='SCHEDULE_NOT_FOUND',
                error_message='Schedule not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_UPDATE_ERROR',
                error_message=f'Error updating schedule: {str(e)}',
                status_code=500
            )

    @swagger_auto_schema(
        operation_description="Delete schedule slot (owner only)",
        responses={
            200: 'Schedule deleted',
            403: 'No permissions',
            404: 'Schedule not found',
        },
        tags=['Schedule']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            self.perform_destroy(self.get_object())
            
            return self.success_response(
                message='Schedule deleted successfully'
            )
            
        except Schedule.DoesNotExist:
            return self.error_response(
                error_number='SCHEDULE_NOT_FOUND',
                error_message='Schedule not found',
                status_code=404
            )
        except Exception as e:
            return self.error_response(
                error_number='SCHEDULE_DELETE_ERROR',
                error_message=f'Error deleting schedule: {str(e)}',
                status_code=500
            )
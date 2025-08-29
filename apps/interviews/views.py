from core.base.common_imports import *
from .models import Interview, InterviewRequest
from .serializers import (
    InterviewSerializer, InterviewCreateSerializer, InterviewUpdateSerializer,
    InterviewRequestSerializer, InterviewRequestCreateSerializer, InterviewRequestUpdateSerializer
)
from .permissions import InterviewPermissions
from core.google_calendar.service import google_calendar_service
from core.notifications.service import notification_service
from core.mail.tasks import send_email_task
import logging

logger = logging.getLogger(__name__)


class InterviewListCreateView(OptimizedListCreateView, InterviewPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Interview.objects.all()

    def get_serializer_class(self):
        return InterviewCreateSerializer if self.request.method == 'POST' else InterviewSerializer

    @swagger_list_create(
        description="Create new interview request",
        response_schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'service': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'created_at': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        tags=["Interviews"]
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        interview = serializer.save(provider=self.request.user)
        
        # Send notification to admins
        try:
            notification_service.send_to_admins(
                notification_type="PROVIDER_INTERVIEW_REQUEST",
                data={
                    "interview_id": interview.id,
                    "provider_id": interview.provider.id,
                    "provider_username": interview.provider.username,
                    "service_title": interview.service.title
                },
                title="New Interview Request",
                body=f"Provider {interview.provider.username} requested an interview for {interview.service.title}"
            )
        except Exception as e:
            logger.error(f"Failed to send interview notification: {e}")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role in ['super_admin', 'admin']:
            return queryset.select_related('provider', 'service')
        else:
            return queryset.filter(provider=self.request.user).select_related('provider', 'service')


class InterviewDetailView(OptimizedRetrieveUpdateDestroyView, InterviewPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Interview.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InterviewUpdateSerializer
        return InterviewSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role in ['super_admin', 'admin']:
            return queryset.select_related('provider', 'service')
        else:
            return queryset.filter(provider=self.request.user).select_related('provider', 'service')

    @swagger_auto_schema(
        operation_description="Update interview status and schedule",
        request_body=InterviewUpdateSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'scheduled_datetime': openapi.Schema(type=openapi.TYPE_STRING),
                    'google_meet_link': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            404: ERROR_404_SCHEMA
        }
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        interview = self.get_object()
        old_status = interview.status
        
        response = super().patch(request, *args, **kwargs)
        
        if response.status_code == 200:
            new_status = response.data.get('status')
            scheduled_datetime = response.data.get('scheduled_datetime')
            
            # Handle status changes
            if new_status == 'scheduled' and scheduled_datetime:
                self._schedule_interview(interview, scheduled_datetime)
            elif new_status == 'rejected':
                self._send_rejection_notification(interview)
            elif new_status == 'completed':
                self._send_completion_notification(interview)
        
        return response

    def _schedule_interview(self, interview, scheduled_datetime):
        """Schedule interview and create Google Calendar event"""
        try:
            from datetime import datetime
            scheduled_dt = datetime.fromisoformat(scheduled_datetime.replace('Z', '+00:00'))
            
            # Create Google Calendar event
            success, result = google_calendar_service.create_interview_event(
                interview=interview,
                scheduled_datetime=scheduled_dt
            )
            
            if success:
                interview.google_calendar_event_id = result['event_id']
                interview.google_meet_link = result['meet_link']
                interview.save()
                
                # Send notification to provider
                notification_service.send_notification_to_user(
                    user=interview.provider,
                    notification_type="INTERVIEW_SCHEDULED",
                    data={
                        "interview_id": interview.id,
                        "scheduled_datetime": scheduled_datetime,
                        "service_title": interview.service.title
                    },
                    title="Interview Scheduled",
                    body=f"Your interview for {interview.service.title} has been scheduled"
                )
                
                # Send email notification
                send_email_task.delay(
                    to_email=interview.provider.email,
                    subject="Interview Scheduled",
                    template_name="interview_scheduled_email.html",
                    context={
                        'provider_name': interview.provider.username,
                        'service_title': interview.service.title,
                        'scheduled_datetime': scheduled_datetime,
                        'google_meet_link': interview.google_meet_link
                    }
                )
            else:
                logger.error(f"Failed to create Google Calendar event: {result}")
                
        except Exception as e:
            logger.error(f"Error scheduling interview: {e}")

    def _send_rejection_notification(self, interview):
        """Send rejection notification to provider"""
        try:
            notification_service.send_notification_to_user(
                user=interview.provider,
                notification_type="INTERVIEW_REJECTED",
                data={
                    "interview_id": interview.id,
                    "service_title": interview.service.title
                },
                title="Interview Request Rejected",
                body=f"Your interview request for {interview.service.title} has been rejected"
            )
        except Exception as e:
            logger.error(f"Error sending rejection notification: {e}")

    def _send_completion_notification(self, interview):
        """Send completion notification"""
        try:
            notification_service.send_notification_to_user(
                user=interview.provider,
                notification_type="INTERVIEW_COMPLETED",
                data={
                    "interview_id": interview.id,
                    "service_title": interview.service.title
                },
                title="Interview Completed",
                body=f"Your interview for {interview.service.title} has been marked as completed"
            )
        except Exception as e:
            logger.error(f"Error sending completion notification: {e}")


class InterviewRequestListCreateView(OptimizedListCreateView, InterviewPermissions):
    permission_classes = [IsAuthenticated]
    queryset = InterviewRequest.objects.all()

    def get_serializer_class(self):
        return InterviewRequestCreateSerializer if self.request.method == 'POST' else InterviewRequestSerializer

    @swagger_list_create(
        description="Create new interview request",
        response_schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'service': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'message': openapi.Schema(type=openapi.TYPE_STRING),
                'created_at': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        tags=["Interview Requests"]
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        interview_request = serializer.save(provider=self.request.user)
        
        # Send notification to admins
        try:
            notification_service.send_to_admins(
                notification_type="PROVIDER_INTERVIEW_REQUEST",
                data={
                    "request_id": interview_request.id,
                    "provider_id": interview_request.provider.id,
                    "provider_username": interview_request.provider.username,
                    "service_title": interview_request.service.title,
                    "message": interview_request.message
                },
                title="New Interview Request",
                body=f"Provider {interview_request.provider.username} requested an interview for {interview_request.service.title}"
            )
        except Exception as e:
            logger.error(f"Failed to send interview request notification: {e}")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role in ['super_admin', 'admin']:
            return queryset.select_related('provider', 'service')
        else:
            return queryset.filter(provider=self.request.user).select_related('provider', 'service')


class InterviewRequestDetailView(OptimizedRetrieveUpdateDestroyView, InterviewPermissions):
    permission_classes = [IsAuthenticated]
    queryset = InterviewRequest.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InterviewRequestUpdateSerializer
        return InterviewRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role in ['super_admin', 'admin']:
            return queryset.select_related('provider', 'service')
        else:
            return queryset.filter(provider=self.request.user).select_related('provider', 'service')

    @swagger_auto_schema(
        operation_description="Update interview request status",
        request_body=InterviewRequestUpdateSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                    'admin_response': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            404: ERROR_404_SCHEMA
        }
    )
    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        interview_request = self.get_object()
        old_status = interview_request.status
        
        response = super().patch(request, *args, **kwargs)
        
        if response.status_code == 200:
            new_status = response.data.get('status')
            admin_response = response.data.get('admin_response', '')
            
            # Send notification to provider
            if new_status == 'approved':
                self._send_approval_notification(interview_request, admin_response)
            elif new_status == 'rejected':
                self._send_rejection_notification(interview_request, admin_response)
        
        return response

    def _send_approval_notification(self, interview_request, admin_response):
        """Send approval notification to provider"""
        try:
            notification_service.send_notification_to_user(
                user=interview_request.provider,
                notification_type="INTERVIEW_REQUEST_APPROVED",
                data={
                    "request_id": interview_request.id,
                    "service_title": interview_request.service.title,
                    "admin_response": admin_response
                },
                title="Interview Request Approved",
                body=f"Your interview request for {interview_request.service.title} has been approved"
            )
        except Exception as e:
            logger.error(f"Error sending approval notification: {e}")

    def _send_rejection_notification(self, interview_request, admin_response):
        """Send rejection notification to provider"""
        try:
            notification_service.send_notification_to_user(
                user=interview_request.provider,
                notification_type="INTERVIEW_REQUEST_REJECTED",
                data={
                    "request_id": interview_request.id,
                    "service_title": interview_request.service.title,
                    "admin_response": admin_response
                },
                title="Interview Request Rejected",
                body=f"Your interview request for {interview_request.service.title} has been rejected"
            )
        except Exception as e:
            logger.error(f"Error sending rejection notification: {e}")


class TestGoogleMeetView(BaseAPIView):
    """Test endpoint for Google Meet integration"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Test Google Meet integration by sending meeting invite to verified users",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'event_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'meet_link': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    @transaction.atomic
    def post(self, request):
        # Get verified users
        verified_users = User.objects.filter(
            is_active=True,
            is_verified=True
        ).exclude(email='')
        
        if not verified_users.exists():
            return Response({
                'message': 'No verified users found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create test interview event
        from datetime import datetime, timedelta
        test_datetime = datetime.now() + timedelta(hours=1)
        
        success, result = google_calendar_service.create_interview_event(
            user=verified_users.first(),
            scheduled_datetime=test_datetime
        )
        
        if success:
            return Response({
                'message': 'Test Google Meet event created successfully',
                'event_id': result['event_id'],
                'meet_link': result['meet_link'],
                'scheduled_for': test_datetime.isoformat(),
                'recipients_count': verified_users.count()
            })
        else:
            return Response({
                'message': f'Failed to create test event: {result}'
            }, status=status.HTTP_400_BAD_REQUEST)
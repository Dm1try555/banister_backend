from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Booking, Interview
from .serializers import BookingSerializer, BookingCreateSerializer, InterviewSerializer, InterviewCreateSerializer, InterviewUpdateSerializer
from apps.authentication.models import User
from core.base.views import CustomerViewSet, ServiceProviderViewSet, NotificationMixin
from core.base.interview_views import InterviewMixin
from core.google_calendar.service import google_calendar_service

class InterviewViewSet(NotificationMixin, InterviewMixin, ServiceProviderViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Interview.objects.all()
        if user.role == 'service_provider':
            return Interview.objects.filter(service__provider=user)
        if user.role == 'customer':
            return Interview.objects.filter(customer=user)
        return Interview.objects.none()
    
    def check_role_permission(self):
        user = self.request.user
        if user.is_staff or user.role in ['service_provider', 'customer']:
            return
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied("Access denied")
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InterviewCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InterviewUpdateSerializer
        return super().get_serializer_class()
    

    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(provider=request.user)
        self.notify_admins(instance, request.user.email)
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        interview = self.get_object()
        serializer = self.get_serializer(interview, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = self.handle_calendar(interview, serializer.validated_data)
        interview = serializer.save(**data)
        self.send_status_notification(interview)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)
    
    @action(detail=False, methods=['get'])
    def admin_requests(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        return Response(self.get_serializer(Interview.objects.filter(status='pending'), many=True).data)
    
    @action(detail=False, methods=['post'])
    def send_google_meet(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        results = []
        for user in User.objects.filter(email_verified=True):
            try:
                success, event_id = google_calendar_service.create_interview_event(
                    user=user, scheduled_datetime=timezone.now() + timezone.timedelta(hours=1)
                )
                results.append({'user': user.email, 'success': success, 'event_id': event_id})
            except Exception as e:
                results.append({'user': user.email, 'success': False, 'error': str(e)})
        
        return Response({'message': 'Google Meet invitations sent', 'results': results})

class BookingViewSet(CustomerViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    pagination_class = None
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return super().get_serializer_class()
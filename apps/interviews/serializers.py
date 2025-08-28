from core.base.common_imports import *
from core.error_handling import ErrorCode
from .models import Interview, InterviewRequest


class InterviewSerializer(serializers.ModelSerializer):
    provider_username = serializers.CharField(source='provider.username', read_only=True)
    provider_email = serializers.CharField(source='provider.email', read_only=True)
    service_title = serializers.CharField(source='service.title', read_only=True)
    
    class Meta:
        model = Interview
        fields = [
            'id', 'provider', 'provider_username', 'provider_email',
            'service', 'service_title', 'status', 'scheduled_datetime',
            'google_calendar_event_id', 'google_meet_link', 'notes',
            'admin_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'provider_username', 'provider_email', 'service_title',
            'google_calendar_event_id', 'google_meet_link', 'created_at', 'updated_at'
        ]


class InterviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['service', 'notes']
    
    def validate_service(self, value):
        if not value:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        return value


class InterviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['status', 'scheduled_datetime', 'admin_notes']
    
    def validate_status(self, value):
        valid_statuses = ['pending', 'scheduled', 'completed', 'rejected', 'cancelled']
        if value not in valid_statuses:
            ErrorCode.INVALID_DATA.raise_error()
        return value
    
    def validate_scheduled_datetime(self, value):
        if value and value <= timezone.now():
            ErrorCode.INVALID_DATA.raise_error()
        return value


class InterviewRequestSerializer(serializers.ModelSerializer):
    provider_username = serializers.CharField(source='provider.username', read_only=True)
    provider_email = serializers.CharField(source='provider.email', read_only=True)
    service_title = serializers.CharField(source='service.title', read_only=True)
    
    class Meta:
        model = InterviewRequest
        fields = [
            'id', 'provider', 'provider_username', 'provider_email',
            'service', 'service_title', 'status', 'message',
            'admin_response', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'provider_username', 'provider_email', 'service_title',
            'created_at', 'updated_at'
        ]


class InterviewRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewRequest
        fields = ['service', 'message']
    
    def validate_service(self, value):
        if not value:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        return value
    
    def validate_message(self, value):
        if not value or len(value.strip()) == 0:
            ErrorCode.MISSING_REQUIRED_FIELD.raise_error()
        if len(value) > 1000:
            ErrorCode.FIELD_TOO_LONG.raise_error()
        return value


class InterviewRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewRequest
        fields = ['status', 'admin_response']
    
    def validate_status(self, value):
        valid_statuses = ['pending', 'approved', 'rejected']
        if value not in valid_statuses:
            ErrorCode.INVALID_DATA.raise_error()
        return value
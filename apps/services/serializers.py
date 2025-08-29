from core.base.common_imports import *
from core.error_handling import ErrorCode

from .models import Service, Schedule


class ServiceSerializer(OptimizedModelSerializer):
    provider = serializers.SerializerMethodField()
    provider_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Service
        fields = ['id', 'title', 'description', 'price', 'provider', 'provider_name', 'created_at']
        read_only_fields = ['provider', 'provider_name', 'created_at']
    
    def get_provider(self, obj):
        return obj.provider.id if obj.provider else None
    
    def get_provider_name(self, obj):
        return obj.provider.username if obj.provider else None


class ServiceCreateSerializer(OptimizedModelSerializer):
    class Meta:
        model = Service
        fields = ['title', 'description', 'price']

    def validate_price(self, value):
        if value <= 0:
            ErrorCode.INVALID_SERVICE_PRICE.raise_error()
        return value


class ServiceUpdateSerializer(OptimizedModelSerializer):
    class Meta:
        model = Service
        fields = ['title', 'description', 'price']

    def validate_price(self, value):
        if value <= 0:
            ErrorCode.INVALID_SERVICE_PRICE.raise_error()
        return value


class ScheduleSerializer(OptimizedModelSerializer):
    provider = serializers.SerializerMethodField()
    provider_name = serializers.SerializerMethodField()
    service_title = serializers.SerializerMethodField()
    service_provider_name = serializers.SerializerMethodField()
    day_of_week_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'service', 'service_title', 'provider', 'provider_name', 'service_provider_name',
            'day_of_week', 'day_of_week_display', 'start_time', 'end_time', 
            'is_available', 'created_at'
        ]
        read_only_fields = [
            'provider', 'provider_name', 'service_title', 'service_provider_name', 
            'day_of_week_display', 'created_at'
        ]
    
    def get_provider(self, obj):
        return obj.provider.id if obj.provider else None
    
    def get_provider_name(self, obj):
        return obj.provider.username if obj.provider else None
    
    def get_service_title(self, obj):
        return obj.service.title if obj.service else None
    
    def get_service_provider_name(self, obj):
        return obj.service.provider.username if obj.service and obj.service.provider else None
    
    def get_day_of_week_display(self, obj):
        return obj.get_day_of_week_display() if hasattr(obj, 'get_day_of_week_display') else None


class ScheduleCreateSerializer(OptimizedModelSerializer):
    class Meta:
        model = Schedule
        fields = ['service', 'day_of_week', 'start_time', 'end_time', 'is_available']
    
    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        day_of_week = attrs.get('day_of_week')
        
        if start_time and end_time and start_time >= end_time:
            ErrorCode.INVALID_SCHEDULE_TIME.raise_error()
        
        if day_of_week is not None and (day_of_week < 0 or day_of_week > 6):
            ErrorCode.INVALID_SCHEDULE_TIME.raise_error()
        
        return attrs


class ScheduleUpdateSerializer(OptimizedModelSerializer):
    class Meta:
        model = Schedule
        fields = ['day_of_week', 'start_time', 'end_time', 'is_available']
    
    def validate(self, data):
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        day_of_week = data.get('day_of_week')
        
        if start_time and end_time and start_time >= end_time:
            ErrorCode.INVALID_SCHEDULE_TIME.raise_error()
        
        if day_of_week is not None and (day_of_week < 0 or day_of_week > 6):
            ErrorCode.INVALID_SCHEDULE_TIME.raise_error()
        
        return data
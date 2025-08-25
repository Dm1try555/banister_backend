from core.base.common_imports import *
from core.error_handling import ErrorCode

from .models import CustomerDashboard, ProviderDashboard, ManagementDashboard, Issue

class CustomerDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDashboard
        fields = '__all__'

class CustomerDashboardUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDashboard
        fields = '__all__'

class ProviderDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderDashboard
        fields = '__all__'

class ProviderDashboardUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderDashboard
        fields = ['calendar_view_type', 'working_hours_start', 'working_hours_end', 'commission_rate', 'email_notifications', 'sms_notifications', 'vacation_mode', 'vacation_start', 'vacation_end']

    def validate_commission_rate(self, value):
        if value is not None and (value < 0 or value > 100):
            ErrorCode.INVALID_DATA.raise_error()
        return value

    def validate_working_hours_start(self, value):
        if value and self.initial_data.get('working_hours_end'):
            end_time = self.initial_data.get('working_hours_end')
            if value >= end_time:
                ErrorCode.INVALID_SCHEDULE_TIME.raise_error()
        return value

    def validate_working_hours_end(self, value):
        if value and self.initial_data.get('working_hours_start'):
            start_time = self.initial_data.get('working_hours_start')
            if value <= start_time:
                ErrorCode.INVALID_SCHEDULE_TIME.raise_error()
        return value

class ManagementDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementDashboard
        fields = '__all__'

class ManagementDashboardUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementDashboard
        fields = ['total_customers_managed', 'total_issues_resolved', 'total_issues_pending']

    def validate_total_customers_managed(self, value):
        if value is not None and value < 0:
            ErrorCode.INVALID_DATA.raise_error()
        return value

    def validate_total_issues_resolved(self, value):
        if value is not None and value < 0:
            ErrorCode.INVALID_DATA.raise_error()
        return value

    def validate_total_issues_pending(self, value):
        if value is not None and value < 0:
            ErrorCode.INVALID_DATA.raise_error()
        return value

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'
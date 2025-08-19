from rest_framework import serializers
from .models import CustomerDashboard, ProviderDashboard, ManagementDashboard, Issue

class CustomerDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDashboard
        fields = '__all__'

class ProviderDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderDashboard
        fields = '__all__'

class ManagementDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagementDashboard
        fields = '__all__'

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'
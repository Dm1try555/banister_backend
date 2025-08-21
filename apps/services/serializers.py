from rest_framework import serializers
from .models import Service, Schedule

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'description', 'price', 'created_at']

class ServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['title', 'description', 'price']

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'
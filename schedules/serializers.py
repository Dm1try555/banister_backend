from rest_framework import serializers
from .models import Schedule
from authentication.serializers import UserSerializer

class ScheduleSerializer(serializers.ModelSerializer):
    provider = UserSerializer(read_only=True)
    class Meta:
        model = Schedule
        fields = ['id', 'provider', 'date', 'start_time', 'end_time', 'created_at']
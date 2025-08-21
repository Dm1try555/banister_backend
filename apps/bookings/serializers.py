from .models import Booking, Interview
from rest_framework import serializers

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['id', 'customer', 'provider', 'service', 'preferred_date', 'preferred_time', 'scheduled_datetime', 'status', 'notes', 'admin_notes', 'google_calendar_event_id', 'created_at']

class InterviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['preferred_date', 'preferred_time', 'notes', 'customer', 'service']

class InterviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['status', 'scheduled_datetime', 'admin_notes']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'customer', 'service', 'provider', 'location', 'preferred_date', 'preferred_time', 'scheduled_datetime', 'status', 'notes', 'total_price', 'created_at']

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['service', 'preferred_date', 'preferred_time', 'notes']
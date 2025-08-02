from rest_framework import serializers
from .models import Service
from authentication.models import User

class ServiceSerializer(serializers.ModelSerializer):
    # Read-only fields for display
    provider_id = serializers.IntegerField(source='provider.id', read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'provider_id', 'title', 'description', 'price', 'created_at']
        read_only_fields = ['id', 'provider_id', 'created_at']
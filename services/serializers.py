from rest_framework import serializers
from .models import Service
from authentication.serializers import UserSerializer
from authentication.models import User

class ServiceSerializer(serializers.ModelSerializer):
    provider = UserSerializer(read_only=True)
    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='provider'), write_only=True, source='provider'
    )
    class Meta:
        model = Service
        fields = ['id', 'provider', 'provider_id', 'title', 'description', 'price', 'created_at']
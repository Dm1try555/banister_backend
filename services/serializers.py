from rest_framework import serializers
from .models import Service
from authentication.serializers import UserSerializer

class ServiceSerializer(serializers.ModelSerializer):
    provider = UserSerializer(read_only=True)
    class Meta:
        model = Service
        fields = ['id', 'provider', 'title', 'description', 'price', 'created_at']
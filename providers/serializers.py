from rest_framework import serializers
from .models import Provider
from authentication.serializers import UserSerializer

class ProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Provider
        fields = ['id', 'user', 'verified', 'rating']
from rest_framework import serializers
from .models import AdminIssue
from authentication.serializers import UserSerializer

class AdminIssueSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = AdminIssue
        fields = ['id', 'user', 'description', 'status', 'created_at']
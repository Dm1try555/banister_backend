# authentication/serializers.py
from rest_framework import serializers
from .models import User, Profile  
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from providers.models import Provider

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['full_name', 'avatar_url', 'bio']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'role', 'profile']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'phone', 'role', 'password', 'username']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            phone=validated_data.get('phone'),
            role=validated_data['role'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        Profile.objects.create(user=user)
        if user.role == 'provider':
            Provider.objects.create(user=user)  # Create Provider instance for providers
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token
# authentication/serializers.py
from rest_framework import serializers
from .models import User, Profile, VerificationCode, EmailConfirmationCode
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from providers.models import Provider
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.db import IntegrityError
from error_handling.exceptions import InvalidEmailError, AuthenticationError, EmailAlreadyExistsError

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar_url', 'bio']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    profile_photo_url = serializers.SerializerMethodField()
    has_required_profile_photo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'role', 'profile', 'profile_photo_url', 'has_required_profile_photo']

    def get_profile_photo_url(self, obj):
        """Get profile photo URL"""
        return obj.get_profile_photo_url()
    
    def get_has_required_profile_photo(self, obj):
        """Check if user has required profile photo"""
        return obj.has_required_profile_photo()

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        # Update main user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Update profile if it's in the request
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()  # Explicit email validation
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'phone', 'role', 'password', 'confirm_password', 'first_name', 'last_name']
    

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        validated_data.pop('confirm_password')
        role = self._kwargs.get('role', validated_data.pop('role'))
        user = User.objects.create_user(
            email=validated_data['email'],
            phone=validated_data.get('phone'),
            role=role,
            password=validated_data['password']
        )
        Profile.objects.create(user=user, first_name=first_name, last_name=last_name)
        if user.role == 'provider':
            Provider.objects.create(user=user)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        # Get role from request
        requested_role = self.initial_data.get('role')
        # Get user by email (or username)
        user = None
        username_field = self.fields.get(self.username_field)
        if username_field:
            username = attrs.get(self.username_field)
            if username:
                try:
                    user = User.objects.get(**{self.username_field: username})
                except User.DoesNotExist:
                    pass
        try:
            data = super().validate(attrs)
        except Exception:
            raise AuthenticationError('Invalid email or password')
        # Check role
        if user and requested_role and user.role != requested_role:
            raise AuthenticationError(f'User with email {user.email} is registered with role {user.role}. Login with role {requested_role} is not possible.')
        # Add role to response
        if user:
            data['role'] = user.role
        return data

class EmailConfirmationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailConfirmationCode
        fields = ['email', 'code', 'created_at', 'is_used']
        read_only_fields = ['created_at', 'is_used']
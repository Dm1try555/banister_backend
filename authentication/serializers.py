from rest_framework import serializers
from .models import User, Profile, VerificationCode, EmailConfirmationCode
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from providers.models import Provider # Ensure this import is correct and Provider model exists
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.db import IntegrityError
from error_handling.exceptions import InvalidEmailError, AuthenticationError, EmailAlreadyExistsError

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'bio']

    def validate_first_name(self, value):
        """Validate US first name format"""
        if value:
            cleaned = ' '.join(value.split())
            if not cleaned.replace("'", "").replace("-", "").replace(" ", "").isalpha():
                raise serializers.ValidationError(
                    'First name can only contain letters, spaces, hyphens, and apostrophes.'
                )
        return value

    def validate_last_name(self, value):
        """Validate US last name format"""
        if value:
            cleaned = ' '.join(value.split())
            if not cleaned.replace("'", "").replace("-", "").replace(" ", "").isalpha():
                raise serializers.ValidationError(
                    'Last name can only contain letters, spaces, hyphens, and apostrophes.'
                )
        return value

    def validate_bio(self, value):
        """Validate bio length for US standards"""
        if value and len(value) > 500:
            raise serializers.ValidationError('Bio cannot exceed 500 characters.')
        return value

class ProviderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['experience_years', 'hourly_rate'] # Assuming these fields are on the Provider model

class BaseUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    profile_photo_url = serializers.SerializerMethodField()
    has_required_profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'role', 'profile', 'profile_photo_url', 'has_required_profile_photo']

    def validate_email(self, value):
        """Validate email format and uniqueness (except for current user)"""
        if value:
            email_parts = value.split('@')
            if len(email_parts) != 2:
                raise serializers.ValidationError('Please enter a valid email address.')
            
            local_part, domain = email_parts
            if len(local_part) < 1 or len(domain) < 3:
                raise serializers.ValidationError('Please enter a valid email address.')
            
            common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
            if domain.lower() not in common_domains and '.' not in domain:
                raise serializers.ValidationError('Please enter a valid email address.')
            
            # Check uniqueness (excluding current user)
            user = self.context.get('request').user if self.context.get('request') else None
            if user and User.objects.filter(email=value).exclude(id=user.id).exists():
                raise serializers.ValidationError('User with this email already exists.')
            elif not user and User.objects.filter(email=value).exists():
                raise serializers.ValidationError('User with this email already exists.')
        return value

    def validate_phone(self, value):
        """Validate US phone number format - supports all common formats"""
        if not value:
            return value
            
        # Remove all non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, value))
        
        # Check for valid US phone number patterns
        if len(digits_only) == 10:
            # Standard US format: (555) 123-4567
            return value
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            # US with country code: +1 (555) 123-4567
            return value
        elif len(digits_only) == 7:
            # Local number without area code (less common but supported)
            return value
        elif len(digits_only) == 12 and digits_only.startswith('11'):
            # International format with double country code (rare but possible)
            return value
        elif len(digits_only) == 13 and digits_only.startswith('111'):
            # Extended international format (very rare but possible)
            return value
        else:
            raise serializers.ValidationError(
                'Please enter a valid US phone number. '
                'Supported formats:\n'
                '• (555) 123-4567\n'
                '• 555-123-4567\n'
                '• 555.123.4567\n'
                '• 555 123 4567\n'
                '• +1 (555) 123-4567\n'
                '• +1-555-123-4567\n'
                '• 1-555-123-4567\n'
                '• 123-4567 (local number)\n'
                '• 5551234567 (no formatting)'
            )
        return value

    def get_profile_photo_url(self, obj):
        """Get profile photo URL"""
        return obj.get_profile_photo_url()

    def get_has_required_profile_photo(self, obj):
        """Check if user has required profile photo"""
        return obj.has_required_profile_photo()

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)

        # Update main user fields (email, phone, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile if data is provided
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class CustomerUserSerializer(BaseUserSerializer):
    """Serializer for customer users - no provider profile fields"""
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'email', 'phone', 'role', 'profile', 'profile_photo_url', 'has_required_profile_photo']


class ProviderUserSerializer(BaseUserSerializer):
    """Serializer for provider users - includes provider profile fields"""
    provider_profile = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'email', 'phone', 'role', 'profile', 'provider_profile', 'profile_photo_url', 'has_required_profile_photo']

    def get_provider_profile(self, obj):
        """Get provider profile if exists"""
        if obj.role == 'provider':
            try:
                from providers.models import Provider
                provider = Provider.objects.get(user=obj)
                return ProviderProfileSerializer(provider).data
            except Provider.DoesNotExist:
                return None
        return None

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        provider_profile_data = validated_data.pop('provider_profile', None)

        # Update main user fields (email, phone, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile if data is provided
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        # Update provider profile if data is provided
        if provider_profile_data:
            provider_instance, created = Provider.objects.get_or_create(user=instance)
            for attr, value in provider_profile_data.items():
                setattr(provider_instance, attr, value)
            provider_instance.save()

        return instance


class ManagementUserSerializer(BaseUserSerializer):
    """Serializer for management users - no provider profile fields"""
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'email', 'phone', 'role', 'profile', 'profile_photo_url', 'has_required_profile_photo']


# Keep the original UserSerializer for backward compatibility, but make it role-aware
class UserSerializer(BaseUserSerializer):
    """Role-aware user serializer that includes provider_profile only for providers"""
    provider_profile = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'email', 'phone', 'role', 'profile', 'provider_profile', 'profile_photo_url', 'has_required_profile_photo']

    def get_provider_profile(self, obj):
        """Only include provider_profile for provider users"""
        if obj.role == 'provider':
            try:
                from providers.models import Provider
                provider = Provider.objects.get(user=obj)
                return ProviderProfileSerializer(provider).data
            except Provider.DoesNotExist:
                return None
        return None

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        provider_profile_data = validated_data.pop('provider_profile', None)

        # Update main user fields (email, phone, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile if data is provided
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        # Update provider profile only if user is a provider and data is provided
        if instance.role == 'provider' and provider_profile_data:
            provider_instance, created = Provider.objects.get_or_create(user=instance)
            for attr, value in provider_profile_data.items():
                setattr(provider_instance, attr, value)
            provider_instance.save()

        return instance

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField() # Explicit email validation
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True, min_length=1, max_length=50)
    last_name = serializers.CharField(write_only=True, min_length=1, max_length=50)

    class Meta:
        model = User
        fields = ['email', 'phone', 'role', 'password', 'confirm_password', 'first_name', 'last_name']

    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        
        # Check for at least one letter and one number
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError('Password must contain at least one letter.')
        
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError('Password must contain at least one number.')
        
        return value

    def validate_email(self, value):
        """Validate email uniqueness and US format"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('User with this email already exists.')
        
        # Basic email format validation for US standards
        if value:
            email_parts = value.split('@')
            if len(email_parts) != 2:
                raise serializers.ValidationError('Please enter a valid email address.')
            
            local_part, domain = email_parts
            if len(local_part) < 1 or len(domain) < 3:
                raise serializers.ValidationError('Please enter a valid email address.')
            
            # Check for common US email providers
            common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
            if domain.lower() not in common_domains and '.' not in domain:
                raise serializers.ValidationError('Please enter a valid email address.')
        
        return value

    def validate_phone(self, value):
        """Validate US phone number format - supports all common formats"""
        if not value:
            return value
            
        # Remove all non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, value))
        
        # Check for valid US phone number patterns
        if len(digits_only) == 10:
            # Standard US format: (555) 123-4567
            return value
        elif len(digits_only) == 11 and digits_only.startswith('1'):
            # US with country code: +1 (555) 123-4567
            return value
        elif len(digits_only) == 7:
            # Local number without area code (less common but supported)
            return value
        elif len(digits_only) == 12 and digits_only.startswith('11'):
            # International format with double country code (rare but possible)
            return value
        elif len(digits_only) == 13 and digits_only.startswith('111'):
            # Extended international format (very rare but possible)
            return value
        else:
            raise serializers.ValidationError(
                'Please enter a valid US phone number. '
                'Supported formats:\n'
                '• (555) 123-4567\n'
                '• 555-123-4567\n'
                '• 555.123.4567\n'
                '• 555 123 4567\n'
                '• +1 (555) 123-4567\n'
                '• +1-555-123-4567\n'
                '• 1-555-123-4567\n'
                '• 123-4567 (local number)\n'
                '• 5551234567 (no formatting)'
            )
        return value

    def validate_first_name(self, value):
        """Validate US first name format"""
        if value:
            # Remove extra spaces and check for valid characters
            cleaned = ' '.join(value.split())
            if not cleaned.replace("'", "").replace("-", "").replace(" ", "").isalpha():
                raise serializers.ValidationError(
                    'First name can only contain letters, spaces, hyphens, and apostrophes.'
                )
            if len(cleaned) < 1:
                raise serializers.ValidationError('First name cannot be empty.')
        return value

    def validate_last_name(self, value):
        """Validate US last name format"""
        if value:
            # Remove extra spaces and check for valid characters
            cleaned = ' '.join(value.split())
            if not cleaned.replace("'", "").replace("-", "").replace(" ", "").isalpha():
                raise serializers.ValidationError(
                    'Last name can only contain letters, spaces, hyphens, and apostrophes.'
                )
            if len(cleaned) < 1:
                raise serializers.ValidationError('Last name cannot be empty.')
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        validated_data.pop('confirm_password')
        
        # Get role from context or validated_data
        role = self.context.get('role', validated_data.get('role', 'customer'))
        
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

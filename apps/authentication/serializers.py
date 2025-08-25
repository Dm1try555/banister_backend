from core.base.common_imports import *
from core.error_handling import ErrorCode

from .models import User, AdminPermission


class UserBaseSerializer(serializers.ModelSerializer):
    """Base serializer for User model with common fields"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'location', 'profile_photo',
            'email_verified', 'firebase_token', 'stripe_account_id',
            'provider_verified', 'provider_rating', 'provider_hourly_rate',
            'created_at', 'updated_at'
        ]


class UserSerializer(UserBaseSerializer):
    """Read-only serializer for User model"""
    class Meta(UserBaseSerializer.Meta):
        read_only_fields = ['id', 'email_verified', 'provider_verified', 'created_at', 'updated_at']


class UserCreateSerializer(UserBaseSerializer):
    """Serializer for user registration"""
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta(UserBaseSerializer.Meta):
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'role', 'phone_number',
            'location'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            ErrorCode.PASSWORDS_DO_NOT_MATCH.raise_error()

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserUpdateSerializer(UserBaseSerializer):
    """Serializer for updating user profile"""
    class Meta(UserBaseSerializer.Meta):
        fields = ['first_name', 'last_name', 'phone_number', 'location']


class AdminProfileUpdateSerializer(UserBaseSerializer):
    """Serializer for admin profile updates"""
    class Meta(UserBaseSerializer.Meta):
        fields = ['first_name', 'last_name']


class AdminPermissionManageSerializer(serializers.Serializer):
    admin_id = serializers.IntegerField()
    permission_name = serializers.CharField(max_length=100)
    can_access = serializers.BooleanField()


class SendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class ProfilePhotoUploadSerializer(serializers.Serializer):
    photo = serializers.ImageField()
    
    def validate_profile_photo(self, value):
        """Validate profile photo"""
        if value:
            # Maximum file size (5MB)
            if value.size > 5 * 1024 * 1024:
                ErrorCode.FILE_TOO_LARGE.raise_error()
            
            # Allowed file types
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if value.content_type not in allowed_types:
                ErrorCode.INVALID_FILE_TYPE.raise_error()
            
            # Size check
            if value.size == 0:
                ErrorCode.EMPTY_FILE.raise_error()
        
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    new_password_confirm = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password and new_password_confirm and new_password != new_password_confirm:
            ErrorCode.PASSWORDS_DO_NOT_MATCH.raise_error()
        
        return attrs


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class AdminPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPermission
        fields = '__all__'
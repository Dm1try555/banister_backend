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

    def validate_email(self, value):
        """Validate email format and uniqueness"""
        import re
        if value:
            # Basic email format validation: must have @ and domain with at least one dot
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                ErrorCode.INVALID_EMAIL_FORMAT.raise_error()
            
            # Check if email already exists
            if User.objects.filter(email=value).exists():
                ErrorCode.USER_ALREADY_EXISTS.raise_error()
        return value

    def validate_username(self, value):
        """Validate username uniqueness"""
        if value and User.objects.filter(username=value).exists():
            ErrorCode.USER_ALREADY_EXISTS.raise_error()
        return value

    def validate_phone_number(self, value):
        """Validate phone number format and uniqueness"""
        if value:
            import re
            # Allow only digits, spaces, dashes, parentheses, plus sign
            if not re.match(r'^[\d\s\-\(\)\+]+$', value):
                ErrorCode.INVALID_PHONE_FORMAT.raise_error()
            
            # Check if phone number already exists
            if User.objects.filter(phone_number=value).exists():
                ErrorCode.USER_ALREADY_EXISTS.raise_error()
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        # Validate password length
        if password and len(password) < 8:
            ErrorCode.PASSWORD_TOO_WEAK.raise_error()

        # Validate password confirmation
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
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        
        # Validate phone number format (only digits and symbols)
        if phone_number:
            import re
            # Allow only digits, spaces, dashes, parentheses, plus sign
            if not re.match(r'^[\d\s\-\(\)\+]+$', phone_number):
                ErrorCode.INVALID_PHONE_FORMAT.raise_error()
        
        return attrs


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
    
    def validate_email(self, value):
        """Validate email format"""
        import re
        if value:
            # Basic email format validation: must have @ and domain with at least one dot
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                ErrorCode.INVALID_EMAIL_FORMAT.raise_error()
        return value


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4, min_length=4)
    
    def validate_email(self, value):
        """Validate email format"""
        import re
        if value:
            # Basic email format validation: must have @ and domain with at least one dot
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                ErrorCode.INVALID_EMAIL_FORMAT.raise_error()
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email format and existence"""
        import re
        if value:
            # Basic email format validation: must have @ and domain with at least one dot
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                ErrorCode.INVALID_EMAIL_FORMAT.raise_error()
            
            # Check if email exists in the system
            if not User.objects.filter(email=value).exists():
                ErrorCode.EMAIL_NOT_FOUND.raise_error()
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=4, max_length=4)
    new_password = serializers.CharField(min_length=8, write_only=True)
    new_password_confirm = serializers.CharField(min_length=8, write_only=True)
    
    def validate_email(self, value):
        """Validate email format and existence"""
        import re
        if value:
            # Basic email format validation: must have @ and domain with at least one dot
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                ErrorCode.INVALID_EMAIL_FORMAT.raise_error()
            
            # Check if email exists in the system
            if not User.objects.filter(email=value).exists():
                ErrorCode.EMAIL_NOT_FOUND.raise_error()
        return value
    
    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        # Validate password length
        if new_password and len(new_password) < 8:
            ErrorCode.PASSWORD_TOO_WEAK.raise_error()
        
        # Validate password confirmation
        if new_password and new_password_confirm and new_password != new_password_confirm:
            ErrorCode.PASSWORDS_DO_NOT_MATCH.raise_error()
        
        return attrs


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





class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class AdminPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminPermission
        fields = '__all__'
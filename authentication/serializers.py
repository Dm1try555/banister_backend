# authentication/serializers.py
from rest_framework import serializers
from .models import User, Profile, VerificationCode
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from providers.models import Provider
from rest_framework_simplejwt.exceptions import AuthenticationFailed

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar_url', 'bio']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'role', 'profile']

class RegisterSerializer(serializers.ModelSerializer):
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
        user = User.objects.create_user(
            email=validated_data['email'],
            phone=validated_data.get('phone'),
            role=validated_data.get('role', 'customer'),
            password=validated_data['password']
        )
        Profile.objects.create(user=user, first_name=first_name, last_name=last_name)
        if user.role == 'provider':
            Provider.objects.create(user=user)  # Create Provider instance for providers
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        # Получаем роль из запроса
        requested_role = self.initial_data.get('role')
        # Получаем пользователя по email (или username)
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
        except AuthenticationFailed:
            raise AuthenticationFailed({'error': 'Invalid email or password'})
        # Проверка роли
        if user and requested_role and user.role != requested_role:
            raise AuthenticationFailed({'error': f'Пользователь с email {user.email} зарегистрирован с ролью {user.role}. Вход с ролью {requested_role} невозможен.'})
        # Добавляем роль в ответ
        if user:
            data['role'] = user.role
        return data

class QuickRegisterRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError('Email или телефон обязательны')
        return data

class QuickRegisterVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)
    code = serializers.CharField()

    def validate(self, data):
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError('Email или телефон обязательны')
        if not data.get('code'):
            raise serializers.ValidationError('Код обязателен')
        return data
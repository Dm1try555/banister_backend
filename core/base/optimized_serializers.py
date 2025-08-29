"""
Оптимизированные базовые serializers для устранения дублирования кода
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class BaseModelSerializer(serializers.ModelSerializer):
    """Базовый ModelSerializer с общими полями"""
    
    class Meta:
        abstract = True
    
    def validate(self, attrs):
        """Базовая валидация"""
        return super().validate(attrs)


class TimestampedSerializer(BaseModelSerializer):
    """Serializer с полями времени"""
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        abstract = True


class UserSerializer(BaseModelSerializer):
    """Базовый User serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        read_only_fields = ['id', 'username', 'email', 'role', 'is_active']


class UserCreateSerializer(BaseModelSerializer):
    """Serializer для создания пользователя"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role']
    
    def validate(self, attrs):
        """Валидация паролей"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    
    def create(self, validated_data):
        """Создание пользователя с хешированием пароля"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(BaseModelSerializer):
    """Serializer для обновления пользователя"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
    
    def validate(self, attrs):
        """Валидация обновления"""
        return super().validate(attrs)


class SoftDeleteSerializer(BaseModelSerializer):
    """Serializer с поддержкой soft delete"""
    
    is_deleted = serializers.BooleanField(read_only=True)
    
    class Meta:
        abstract = True


class PaginatedSerializer(BaseModelSerializer):
    """Serializer с поддержкой пагинации"""
    
    class Meta:
        abstract = True


class BaseListSerializer(BaseModelSerializer):
    """Базовый serializer для списков"""
    
    class Meta:
        abstract = True


class BaseDetailSerializer(BaseModelSerializer):
    """Базовый serializer для деталей"""
    
    class Meta:
        abstract = True


class BaseCreateSerializer(BaseModelSerializer):
    """Базовый serializer для создания"""
    
    class Meta:
        abstract = True


class BaseUpdateSerializer(BaseModelSerializer):
    """Базовый serializer для обновления"""
    
    class Meta:
        abstract = True


class BaseDeleteSerializer(BaseModelSerializer):
    """Базовый serializer для удаления"""
    
    class Meta:
        abstract = True


class OptimizedModelSerializer(BaseModelSerializer):
    """Оптимизированный ModelSerializer с общими методами"""
    
    def get_field_names(self, declared_fields, info):
        """Автоматическое получение полей"""
        fields = super().get_field_names(declared_fields, info)
        if hasattr(self.Meta, 'exclude_fields'):
            fields = [f for f in fields if f not in self.Meta.exclude_fields]
        return fields
    
    def validate_required_fields(self, attrs):
        """Валидация обязательных полей"""
        required_fields = getattr(self.Meta, 'required_fields', [])
        for field in required_fields:
            if field not in attrs or not attrs[field]:
                raise serializers.ValidationError(f"{field} is required")
        return attrs
    
    def validate(self, attrs):
        """Общая валидация"""
        attrs = self.validate_required_fields(attrs)
        return super().validate(attrs)
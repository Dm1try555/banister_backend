"""
Оптимизированные базовые permissions для устранения дублирования кода
"""

from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseRolePermission(BasePermission):
    """Базовый класс для ролевых permissions"""
    
    allowed_roles = []
    
    def has_permission(self, request, view):
        """Проверка разрешения на основе роли"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not self.allowed_roles:
            return True
        
        return request.user.role in self.allowed_roles


class AdminOnlyPermission(BaseRolePermission):
    """Permission только для админов"""
    allowed_roles = ['admin', 'super_admin']


class SuperAdminOnlyPermission(BaseRolePermission):
    """Permission только для суперадминов"""
    allowed_roles = ['super_admin']


class ProviderPermission(BaseRolePermission):
    """Permission для провайдеров"""
    allowed_roles = ['service_provider', 'admin', 'super_admin']


class CustomerPermission(BaseRolePermission):
    """Permission для клиентов"""
    allowed_roles = ['customer', 'admin', 'super_admin']


class StaffPermission(BaseRolePermission):
    """Permission для персонала"""
    allowed_roles = ['hr', 'supervisor', 'admin', 'super_admin']


class OptimizedPermissionMixin:
    """Mixin для оптимизации permissions"""
    
    def get_permissions(self):
        """Получение permissions на основе действия"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [AdminOnlyPermission]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [BaseRolePermission]
        else:
            permission_classes = [AdminOnlyPermission]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset_permissions(self):
        """Получение permissions для queryset"""
        if self.request.user.role == 'super_admin':
            return self.queryset.all()
        elif self.request.user.role == 'admin':
            return self.queryset.filter(is_active=True)
        else:
            return self.queryset.filter(user=self.request.user)


class BaseObjectPermission(BasePermission):
    """Базовый класс для object permissions"""
    
    def has_object_permission(self, request, view, obj):
        """Проверка разрешения на объект"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Суперадмин может все
        if request.user.role == 'super_admin':
            return True
        
        # Админ может все активные объекты
        if request.user.role == 'admin':
            return getattr(obj, 'is_active', True)
        
        # Пользователь может только свои объекты
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class OwnerPermission(BaseObjectPermission):
    """Permission для владельца объекта"""
    
    def has_object_permission(self, request, view, obj):
        """Проверка владения объектом"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Суперадмин может все
        if request.user.role == 'super_admin':
            return True
        
        # Админ может все активные объекты
        if request.user.role == 'admin':
            return getattr(obj, 'is_active', True)
        
        # Проверка владения
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'customer'):
            return obj.customer == request.user
        elif hasattr(obj, 'provider'):
            return obj.provider == request.user
        elif hasattr(obj, 'sender'):
            return obj.sender == request.user
        
        return False


class OptimizedPermission(BasePermission):
    """Оптимизированный permission с кэшированием"""
    
    def __init__(self):
        self._cache = {}
    
    def has_permission(self, request, view):
        """Проверка разрешения с кэшированием"""
        cache_key = f"{request.user.id}_{view.__class__.__name__}_{view.action}"
        
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._check_permission(request, view)
        self._cache[cache_key] = result
        return result
    
    def _check_permission(self, request, view):
        """Реальная проверка разрешения"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Суперадмин может все
        if request.user.role == 'super_admin':
            return True
        
        # Админ может все кроме суперадминских функций
        if request.user.role == 'admin':
            return view.action not in ['destroy_superadmin', 'create_superadmin']
        
        # Обычные пользователи могут только свои данные
        return view.action in ['list', 'retrieve', 'update', 'partial_update']


class RoleBasedPermission(BasePermission):
    """Permission на основе роли с гибкой настройкой"""
    
    role_permissions = {
        'super_admin': ['*'],  # Все действия
        'admin': ['list', 'retrieve', 'create', 'update', 'partial_update'],
        'service_provider': ['list', 'retrieve', 'update', 'partial_update'],
        'customer': ['list', 'retrieve', 'create', 'update', 'partial_update'],
        'hr': ['list', 'retrieve', 'update', 'partial_update'],
        'supervisor': ['list', 'retrieve', 'update', 'partial_update'],
    }
    
    def has_permission(self, request, view):
        """Проверка разрешения на основе роли"""
        if not request.user or not request.user.is_authenticated:
            return False
        
        user_role = request.user.role
        action = getattr(view, 'action', 'list')
        
        if user_role not in self.role_permissions:
            return False
        
        allowed_actions = self.role_permissions[user_role]
        
        # Суперадмин может все
        if '*' in allowed_actions:
            return True
        
        return action in allowed_actions
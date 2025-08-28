from django.db import transaction
from rest_framework.response import Response
from core.error_handling.enums import ErrorCode


class OptimizedCRUDMixin:
    """Mixin для оптимизации CRUD операций и устранения дублирования кода"""
    
    def get_permission_action(self):
        """Получить действие для проверки разрешений"""
        action_map = {
            'PUT': 'edit',
            'PATCH': 'edit', 
            'DELETE': 'delete'
        }
        return action_map.get(self.request.method)
    
    def check_crud_permission(self, model_name):
        """Проверить разрешение для CRUD операции"""
        action = self.get_permission_action()
        if action:
            permission_name = f"{action}_{model_name}"
            self.check_permission(permission_name)
    
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        """Оптимизированный PUT метод"""
        model_name = self.get_model_name()
        self.check_crud_permission(model_name)
        return super().put(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        """Оптимизированный PATCH метод"""
        model_name = self.get_model_name()
        self.check_crud_permission(model_name)
        return super().patch(request, *args, **kwargs)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """Оптимизированный DELETE метод"""
        model_name = self.get_model_name()
        self.check_crud_permission(model_name)
        return super().delete(request, *args, **kwargs)
    
    def get_model_name(self):
        """Получить имя модели для проверки разрешений"""
        if hasattr(self, 'model'):
            return self.model.__name__.lower()
        elif hasattr(self, 'queryset') and self.queryset:
            return self.queryset.model.__name__.lower()
        else:
            return 'object'


class OptimizedListMixin:
    """Mixin для оптимизации списковых представлений"""
    
    def get_optimized_queryset(self):
        """Получить оптимизированный queryset с select_related"""
        if hasattr(self, 'select_related_fields'):
            return self.queryset.select_related(*self.select_related_fields)
        return self.queryset
    
    def get_queryset(self):
        """Переопределить get_queryset для применения оптимизаций"""
        queryset = super().get_queryset()
        return self.get_optimized_queryset()


class OptimizedDetailMixin:
    """Mixin для оптимизации детальных представлений"""
    
    def get_optimized_queryset(self):
        """Получить оптимизированный queryset с select_related"""
        if hasattr(self, 'select_related_fields'):
            return self.queryset.select_related(*self.select_related_fields)
        return self.queryset
    
    def get_queryset(self):
        """Переопределить get_queryset для применения оптимизаций"""
        queryset = super().get_queryset()
        return self.get_optimized_queryset()
from core.base.common_imports import *


class RoleBase:
    def _get_user_queryset(self, model, user):
        if user.is_staff:
            return model.objects.all()
        if user.role == 'customer' and hasattr(model, 'customer'):
            return model.objects.filter(customer=user)
        if user.role == 'service_provider' and hasattr(model, 'provider'):
            return model.objects.filter(provider=user)
        return model.objects.none()
    
    def _get_admin_queryset(self, model, user):
        if not user.is_staff:
            return model.objects.none()
        return model.objects.all()
    
    def _get_service_provider_queryset(self, model, user):
        return self._get_user_queryset(model, user) if user.role == 'service_provider' else self._get_admin_queryset(model, user)
    
    def _get_customer_queryset(self, model, user):
        return self._get_user_queryset(model, user) if user.role == 'customer' else self._get_admin_queryset(model, user)

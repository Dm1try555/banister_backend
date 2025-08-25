class BasePermissionsMixin:
    """Base permissions mixin"""
    
    def get_user_role(self):
        """Get user role"""
        if not self.request.user.is_authenticated:
            return 'anonymous'
        return self.request.user.role
    
    def can_perform_action(self, action_name):
        """Check if user can perform action"""
        role = self.get_user_role()
        method_name = f"can_{action_name}"
        
        if hasattr(self, method_name):
            return getattr(self, method_name)(role)
        
        # By default - only for registered users
        return role != 'anonymous'
    
    def check_permission(self, action_name):
        """Check permission and raise error if no permission"""
        if not self.can_perform_action(action_name):
            from core.error_handling.enums import ErrorCode
            ErrorCode.PERMISSION_DENIED.raise_error()


class RoleBasedQuerysetMixin:
    """Automatically filter queryset based on user role"""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_authenticated:
            return self._get_anonymous_queryset(queryset)
        
        # For User model - special logic
        if hasattr(queryset.model, 'role'):
            return self._filter_users_by_role(queryset, user)
        
        # For other models - by customer/provider/user fields
        if hasattr(queryset.model, 'customer'):
            return self._filter_objects_by_customer_field(queryset, user)
        elif hasattr(queryset.model, 'provider'):
            return self._filter_objects_by_provider_field(queryset, user)
        elif hasattr(queryset.model, 'user'):
            return self._filter_objects_by_user_field(queryset, user)
        
        return queryset
    
    def _get_anonymous_queryset(self, queryset):
        """Queryset for anonymous users (only public data)"""
        # By default - only public data
        if hasattr(queryset.model, 'is_public'):
            return queryset.filter(is_public=True)
        elif hasattr(queryset.model, 'is_active'):
            return queryset.filter(is_active=True)
        return queryset.model.objects.none()
    
    def _filter_users_by_role(self, queryset, user):
        """Filter users by roles (for User model)"""
        if user.role == 'super_admin':
            return queryset.all()
        elif user.role == 'admin':
            return queryset.exclude(role='super_admin')
        elif user.role == 'hr':
            return queryset.filter(role__in=['supervisor', 'customer', 'service_provider'])
        elif user.role == 'supervisor':
            return queryset.filter(role__in=['customer', 'service_provider'])
        else:
            return queryset.filter(role=user.role)
    
    def _filter_objects_by_customer_field(self, queryset, user):
        """Filter objects by customer field (e.g. bookings, interviews)"""
        if user.role in ['super_admin', 'admin', 'hr', 'supervisor']:
            return queryset.all()
        elif user.role == 'customer':
            return queryset.filter(customer=user)
        else:
            return queryset.none()
    
    def _filter_objects_by_provider_field(self, queryset, user):
        """Filter objects by provider field (e.g. services, schedules)"""
        if user.role in ['super_admin', 'admin', 'hr']:
            return queryset.all()
        elif user.role == 'service_provider':
            return queryset.filter(provider=user)
        else:
            return queryset.all()  # Customer can see all services
    
    def _filter_objects_by_user_field(self, queryset, user):
        """Filter objects by user field (e.g. documents, notifications)"""
        if user.role in ['super_admin', 'admin', 'hr', 'supervisor']:
            return queryset.all()
        else:
            return queryset.filter(user=user) 
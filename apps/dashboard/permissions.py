"""
Разрешения для приложения Dashboard
"""

from core.base.permissions import BasePermissionsMixin


class DashboardPermissions(BasePermissionsMixin):
    """Permissions for dashboards"""
    
    def can_view_customer_dashboard(self, role):
        """Who can view customer dashboard"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'customer']
    
    def can_edit_customer_dashboard(self, role):
        """Who can edit customer dashboard"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'customer']
    
    def can_view_provider_dashboard(self, role):
        """Who can view provider dashboard"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'service_provider']
    
    def can_edit_provider_dashboard(self, role):
        """Who can edit provider dashboard"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor', 'service_provider']
    
    def can_view_management_dashboard(self, role):
        """Who can view management dashboard"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_edit_management_dashboard(self, role):
        """Who can edit management dashboard"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor'] 
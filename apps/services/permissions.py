from core.base.permissions import BasePermissionsMixin


class ServicePermissions(BasePermissionsMixin):
    """Permissions for services"""
    
    def can_view_services(self, role):
        """Who can view services"""
        # All can view services (including unauthorized)
        return True
    
    def can_create_service(self, role):
        """Who can create services"""
        return role in ['super_admin', 'admin', 'hr', 'service_provider']
    
    def can_edit_service(self, role):
        """Who can edit services"""
        return role in ['super_admin', 'admin', 'hr', 'service_provider']
    
    def can_delete_service(self, role):
        """Who can delete services"""
        return role in ['super_admin', 'admin', 'hr', 'service_provider']
    
    def can_view_service_details(self, role):
        """Who can view service details"""
        # All can view details
        return True


class SchedulePermissions(BasePermissionsMixin):
    """Permissions for schedules"""
    
    def can_view_schedules(self, role):
        """Who can view schedules"""
        # All can view schedules
        return True
    
    def can_create_schedule(self, role):
        """Who can create schedules"""
        return role in ['super_admin', 'admin', 'hr', 'service_provider']
    
    def can_edit_schedule(self, role):
        """Who can edit schedules"""
        return role in ['super_admin', 'admin', 'hr', 'service_provider']
    
    def can_delete_schedule(self, role):
        """Who can delete schedules"""
        return role in ['super_admin', 'admin', 'hr', 'service_provider']
    
    def can_view_schedule_details(self, role):
        """Who can view schedule details"""
        # All can view details
        return True 
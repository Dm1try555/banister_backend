from core.base.permissions import BasePermissionsMixin


class NotificationPermissions(BasePermissionsMixin):
    """Permissions for notifications"""
    
    def can_view_notifications(self, role):
        """Who can view notifications"""
        return role != 'anonymous'
    
    def can_send_notifications(self, role):
        """Who can send notifications"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_edit_notifications(self, role):
        """Who can edit notifications"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_delete_notifications(self, role):
        """Who can delete notifications"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_mark_as_read(self, role):
        """Who can mark notifications as read"""
        return role != 'anonymous'
    
    def can_view_all_notifications(self, role):
        """Who can view all notifications"""
        return role != 'anonymous'
    
    def can_manage_notification_settings(self, role):
        """Who can manage notification settings"""
        return role != 'anonymous' 
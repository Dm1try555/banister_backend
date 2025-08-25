from core.base.permissions import BasePermissionsMixin


class ChatPermissions(BasePermissionsMixin):
    """Permissions for chat"""
    
    def can_view_chat(self, role):
        """Who can view chat"""
        return role != 'anonymous'
    
    def can_send_messages(self, role):
        """Who can send messages"""
        return role != 'anonymous'
    
    def can_edit_messages(self, role):
        """Who can edit messages"""
        return role != 'anonymous'
    
    def can_delete_messages(self, role):
        """Who can delete messages"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_create_chat_room(self, role):
        """Who can create chat rooms"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_manage_chat_room(self, role):
        """Who can manage chat rooms"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_view_chat_history(self, role):
        """Who can view chat history"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_block_users(self, role):
        """Who can block users"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor'] 
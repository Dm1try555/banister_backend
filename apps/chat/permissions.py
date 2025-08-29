from core.base.common_imports import *


class ChatPermissions(BasePermissionsMixin):
    """Permissions for chat"""
    
    # Роли с доступом к чату
    CHAT_ROLES = ['customer', 'service_provider', 'admin', 'hr', 'supervisor', 'super_admin']
    MODERATOR_ROLES = ['admin', 'hr', 'supervisor', 'super_admin']
    ADMIN_ROLES = ['admin', 'super_admin']
    
    def can_view_chat(self, role):
        """Who can view chat"""
        return role in self.CHAT_ROLES
    
    def can_send_messages(self, role):
        """Who can send messages"""
        return role in self.CHAT_ROLES
    
    def can_edit_messages(self, role):
        """Who can edit messages"""
        return role in self.CHAT_ROLES
    
    def can_delete_messages(self, role):
        """Who can delete messages"""
        return role in self.MODERATOR_ROLES
    
    def can_create_chat_room(self, role):
        """Who can create chat rooms"""
        return role in self.MODERATOR_ROLES
    
    def can_manage_chat_room(self, role):
        """Who can manage chat rooms"""
        return role in self.MODERATOR_ROLES
    
    def can_view_chat_history(self, role):
        """Who can view chat history"""
        return role in self.MODERATOR_ROLES
    
    def can_block_users(self, role):
        """Who can block users"""
        return role in self.MODERATOR_ROLES 
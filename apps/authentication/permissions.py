from core.base.permissions import BasePermissionsMixin


class UserPermissions(BasePermissionsMixin):
    """Permissions for users"""
    
    def can_view_users(self, role):
        """Who can view users"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_create_user(self, role):
        """Who can create users"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_edit_user(self, role):
        """Who can edit users"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_delete_user(self, role):
        """Who can delete users"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_view_user_details(self, role):
        """Who can view user details"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_manage_roles(self, role):
        """Who can manage roles"""
        return role in ['super_admin', 'admin']
    
    def can_verify_provider(self, role):
        """Who can verify providers"""
        return role in ['super_admin', 'admin', 'hr']


class ProfilePermissions(BasePermissionsMixin):
    """Permissions for profiles"""
    
    def can_view_own_profile(self, role):
        """Who can view own profile"""
        return role != 'anonymous'
    
    def can_edit_own_profile(self, role):
        """Who can edit own profile"""
        return role != 'anonymous'
    
    def can_delete_own_profile(self, role):
        """Who can delete own profile"""
        return role != 'anonymous'
    
    def can_upload_photo(self, role):
        """Who can upload profile photo"""
        return role != 'anonymous'
    
    def can_view_other_profiles(self, role):
        """Who can view other profiles"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor'] 
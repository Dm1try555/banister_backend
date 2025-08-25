from core.base.permissions import BasePermissionsMixin


class WithdrawalPermissions(BasePermissionsMixin):
    """Permissions for withdrawals"""
    
    def can_view_withdrawals(self, role):
        """Who can view withdrawals"""
        return role != 'anonymous'
    
    def can_create_withdrawal(self, role):
        """Who can create withdrawal requests"""
        return role in ['super_admin', 'admin', 'hr', 'service_provider']
    
    def can_edit_withdrawal(self, role):
        """Who can edit withdrawals"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_delete_withdrawal(self, role):
        """Who can delete withdrawals"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_approve_withdrawal(self, role):
        """Who can approve withdrawals"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_reject_withdrawal(self, role):
        """Who can reject withdrawals"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_view_withdrawal_details(self, role):
        """Who can view withdrawal details"""
        return role != 'anonymous'
    
    def can_view_all_withdrawals(self, role):
        """Who can view all withdrawals"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_manage_withdrawal_settings(self, role):
        """Who can manage withdrawal settings"""
        return role in ['super_admin', 'admin'] 
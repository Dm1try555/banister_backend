from core.base.permissions import BasePermissionsMixin


class PaymentPermissions(BasePermissionsMixin):
    """Permissions for payments"""
    
    def can_view_payments(self, role):
        """Who can view payments"""
        # Only registered users
        return role != 'anonymous'
    
    def can_create_payment(self, role):
        """Who can create payments"""
        return role in ['super_admin', 'admin', 'hr', 'customer']
    
    def can_edit_payment(self, role):
        """Who can edit payments"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_delete_payment(self, role):
        """Who can delete payments"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_view_payment_details(self, role):
        """Who can view payment details"""
        # Only registered users
        return role != 'anonymous'
    
    def can_confirm_payment(self, role):
        """Who can confirm payments"""
        return role in ['super_admin', 'admin', 'hr', 'customer']
    
    def can_transfer_payment(self, role):
        """Who can transfer payments"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_refund_payment(self, role):
        """Who can refund payments"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_view_payment_history(self, role):
        """Who can view payment history"""
        # Only registered users
        return role != 'anonymous' 
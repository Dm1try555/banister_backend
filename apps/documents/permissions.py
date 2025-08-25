from core.base.permissions import BasePermissionsMixin


class DocumentPermissions(BasePermissionsMixin):
    """Permissions for documents"""
    
    def can_view_documents(self, role):
        """Who can view documents"""
        return role != 'anonymous'
    
    def can_upload_documents(self, role):
        """Who can upload documents"""
        return role != 'anonymous'
    
    def can_edit_documents(self, role):
        """Who can edit documents"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_delete_documents(self, role):
        """Who can delete documents"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_verify_documents(self, role):
        """Who can verify documents"""
        return role in ['super_admin', 'admin', 'hr']
    
    def can_view_all_documents(self, role):
        """Who can view all documents"""
        return role in ['super_admin', 'admin', 'hr', 'supervisor']
    
    def can_download_documents(self, role):
        """Who can download documents"""
        return role != 'anonymous' 
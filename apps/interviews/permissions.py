from core.base.permissions import BasePermissionsMixin


class InterviewPermissions(BasePermissionsMixin):
    """Permissions for interview-related operations"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Allow all authenticated users to view their own interviews
        if request.method in ['GET']:
            return True
        
        # Only providers can create interview requests
        if request.method == 'POST' and view.action in ['create']:
            return request.user.role in ['provider']
        
        # Only admins can update interview status
        if request.method in ['PUT', 'PATCH'] and view.action in ['update', 'partial_update']:
            return request.user.role in ['super_admin', 'admin']
        
        # Only admins can delete interviews
        if request.method == 'DELETE':
            return request.user.role in ['super_admin', 'admin']
        
        return False
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Users can view their own interviews
        if request.method in ['GET']:
            if hasattr(obj, 'provider'):
                return obj.provider == request.user
            elif hasattr(obj, 'provider'):
                return obj.provider == request.user
        
        # Only admins can update/delete interviews
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.role in ['super_admin', 'admin']
        
        return False
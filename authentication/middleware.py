import re
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from authentication.models import AdminPermission
import logging

logger = logging.getLogger(__name__)


class SwaggerAuthMiddleware(MiddlewareMixin):
    """
    Middleware for automatically adding "Bearer" to tokens in Swagger UI
    """
    
    def process_request(self, request):
        # Check if this is an API request
        if request.path.startswith('/api/'):
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            print(f"Auth header: {auth_header}")
            
            # If token exists but doesn't start with "Bearer"
            if auth_header and not auth_header.startswith('Bearer '):
                # Check if it looks like a JWT token (3 parts separated by dots)
                token_pattern = r'^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$'
                if re.match(token_pattern, auth_header.strip()):
                    # Add "Bearer " to the token
                    request.META['HTTP_AUTHORIZATION'] = f'Bearer {auth_header.strip()}'
                    print(f"Added Bearer to token: {auth_header[:20]}...")
                else:
                    print(f"Token doesn't match pattern: {auth_header}")
            elif auth_header.startswith('Bearer '):
                print(f"Token already has Bearer: {auth_header[:30]}...")
            else:
                print("No auth header found")
        
        return None 


class AdminPermissionMiddleware:
    """
    Middleware to check admin permissions for specific endpoints
    """
    
    # Define permission mappings for different endpoints
    PERMISSION_MAPPINGS = {
        # User Management
        '/api/auth/admin/list/': ['user_management', 'admin_management'],
        '/api/auth/admin/profile/update/': ['user_management', 'admin_management'],
        
        # Service Management
        '/api/services/': ['service_management'],
        '/api/providers/': ['service_management'],
        
        # Booking Management
        '/api/bookings/': ['booking_management'],
        '/api/schedules/': ['booking_management'],
        
        # Payment Management
        '/api/payments/': ['payment_management'],
        '/api/withdrawals/': ['payment_management', 'withdrawal_management'],
        
        # Document Management
        '/api/documents/': ['document_management'],
        '/api/file-storage/': ['document_management'],
        
        # Financial Reports
        '/api/dashboard/financial/': ['financial_reports'],
        '/api/reports/': ['financial_reports'],
        
        # System Settings
        '/api/admin/settings/': ['system_settings'],
        '/api/admin/config/': ['system_settings'],
        
        # Admin Management
        '/api/auth/admin/permissions/': ['admin_management'],
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated and has admin role
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.is_admin_role():
                # Check permissions for admin endpoints
                if not self._has_required_permissions(request):
                    return JsonResponse({
                        'error': 'Access denied. Insufficient permissions.',
                        'message': 'You do not have the required permissions to access this endpoint.'
                    }, status=403)
        
        response = self.get_response(request)
        return response
    
    def _has_required_permissions(self, request):
        """
        Check if the admin user has required permissions for the current endpoint
        """
        # Skip permission check for super admin
        if request.user.is_super_admin():
            return True
        
        # Get the current path
        path = request.path_info
        
        # Find required permissions for this path
        required_permissions = []
        for endpoint, permissions in self.PERMISSION_MAPPINGS.items():
            if path.startswith(endpoint):
                required_permissions.extend(permissions)
        
        # If no specific permissions required, allow access
        if not required_permissions:
            return True
        
        # Get user's active permissions
        user_permissions = AdminPermission.objects.filter(
            admin_user=request.user,
            is_active=True
        ).values_list('permission', flat=True)
        
        # Check if user has at least one of the required permissions
        has_permission = any(perm in user_permissions for perm in required_permissions)
        
        if not has_permission:
            logger.warning(
                f"Admin {request.user.email} (ID: {request.user.id}) attempted to access {path} "
                f"but lacks required permissions: {required_permissions}. "
                f"User has permissions: {list(user_permissions)}"
            )
        
        return has_permission


class AdminActivityLoggingMiddleware:
    """
    Middleware to log admin activities for audit purposes
    """
    
    ADMIN_ENDPOINTS = [
        '/api/auth/admin/',
        '/api/services/',
        '/api/providers/',
        '/api/bookings/',
        '/api/payments/',
        '/api/withdrawals/',
        '/api/documents/',
        '/api/dashboard/',
        '/api/reports/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log admin activities
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.is_admin_role():
                self._log_admin_activity(request)
        
        response = self.get_response(request)
        return response
    
    def _log_admin_activity(self, request):
        """
        Log admin activities for audit purposes
        """
        try:
            path = request.path_info
            method = request.method
            
            # Check if this is an admin endpoint
            is_admin_endpoint = any(path.startswith(endpoint) for endpoint in self.ADMIN_ENDPOINTS)
            
            if is_admin_endpoint and method in ['POST', 'PUT', 'DELETE']:
                logger.info(
                    f"Admin Activity: {request.user.email} (ID: {request.user.id}, Role: {request.user.role}) "
                    f"performed {method} on {path}"
                )
                
                # Log additional details for sensitive operations
                if 'permissions' in path or 'admin' in path:
                    logger.info(
                        f"Admin Management Activity: {request.user.email} performed {method} on {path} "
                        f"with data: {request.data if hasattr(request, 'data') else 'No data'}"
                    )
        
        except Exception as e:
            logger.error(f"Error logging admin activity: {str(e)}")


class RoleBasedAccessMiddleware:
    """
    Middleware to enforce role-based access control
    """
    
    ROLE_ENDPOINTS = {
        'super_admin': [
            '/api/auth/admin/permissions/',
            '/api/auth/admin/list/',
            '/api/admin/settings/',
        ],
        'admin': [
            '/api/services/',
            '/api/providers/',
            '/api/bookings/',
            '/api/payments/',
            '/api/withdrawals/',
            '/api/documents/',
        ],
        'accountant': [
            '/api/payments/',
            '/api/withdrawals/',
            '/api/dashboard/financial/',
            '/api/reports/',
        ],
        'management': [
            '/api/customers/',
            '/api/support/',
            '/api/bookings/',
            '/api/messages/',
        ],
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check role-based access
        if hasattr(request, 'user') and request.user.is_authenticated:
            if not self._has_role_access(request):
                return JsonResponse({
                    'error': 'Access denied. Insufficient role privileges.',
                    'message': 'Your role does not have permission to access this endpoint.'
                }, status=403)
        
        response = self.get_response(request)
        return response
    
    def _has_role_access(self, request):
        """
        Check if the user's role has access to the current endpoint
        """
        path = request.path_info
        user_role = request.user.role
        
        # Super admin has access to everything
        if user_role == 'super_admin':
            return True
        
        # Check if user's role has access to this endpoint
        if user_role in self.ROLE_ENDPOINTS:
            allowed_endpoints = self.ROLE_ENDPOINTS[user_role]
            has_access = any(path.startswith(endpoint) for endpoint in allowed_endpoints)
            
            if not has_access:
                logger.warning(
                    f"User {request.user.email} (Role: {user_role}) attempted to access {path} "
                    f"but role does not have permission"
                )
            
            return has_access
        
        # If role not in mapping, deny access
        logger.warning(
            f"User {request.user.email} (Role: {user_role}) attempted to access {path} "
            f"but role is not mapped for access control"
        )
        return False 
import re
from django.utils.deprecation import MiddlewareMixin


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
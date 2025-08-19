from rest_framework.views import exception_handler
from rest_framework.response import Response
from ..exceptions import CustomAPIException


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if isinstance(exc, CustomAPIException):
        custom_response_data = {
            'error': {
                'code': exc.error_code.code,
                'title': exc.error_code.title,
                'description': str(exc.detail),
                'timestamp': None
            }
        }
        
        return Response(custom_response_data, status=exc.status_code)
    
    # For standard DRF exceptions, format them consistently
    if response is not None:
        custom_response_data = {
            'error': {
                'code': response.status_code,
                'title': exc.__class__.__name__,
                'description': str(response.data.get('detail', response.data)) if hasattr(response.data, 'get') else str(response.data),
                'timestamp': None
            }
        }
        
        response.data = custom_response_data
    
    return response
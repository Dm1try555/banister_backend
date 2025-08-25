from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# ============================================================================
# БАЗОВЫЕ СХЕМЫ ОШИБОК
# ============================================================================

ERROR_400_SCHEMA = openapi.Response(
    description="Validation errors",
    examples={
        "application/json": {
            "1012: Passwords do not match": {
                "statusCode": 400,
                "errorCode": 1012,
                "exceptionType": "ValidationException",
                "message": "1012: Passwords do not match",
                "error": "Password and password confirmation do not match",
                "timestamp": "2025-08-24T07:47:24.123456+00:00",
                "endpoint": "/api/v1/auth/register/",
                "method": "POST"
            },
            "1013: File too large": {
                "statusCode": 400,
                "errorCode": 1013,
                "exceptionType": "ValidationException",
                "message": "1013: File too large",
                "error": "File size exceeds maximum allowed limit",
                "timestamp": "2025-08-24T07:47:24.123456+00:00",
                "endpoint": "/api/v1/auth/profile/photo/",
                "method": "POST"
            }
        }
    }
)

ERROR_401_SCHEMA = openapi.Response(
    description="Authentication required",
    examples={
        "application/json": {
            "1003: Token expired": {
                "statusCode": 401,
                "errorCode": 1003,
                "exceptionType": "AuthenticationException",
                "message": "1003: Token expired",
                "error": "Authentication token has expired",
                "timestamp": "2025-08-24T07:47:24.123456+00:00",
                "endpoint": "/api/v1/auth/profile/",
                "method": "GET"
            }
        }
    }
)

ERROR_403_SCHEMA = openapi.Response(
    description="Permission denied",
    examples={
        "application/json": {
            "1005: Permission denied": {
                "statusCode": 403,
                "errorCode": 1005,
                "exceptionType": "PermissionException",
                "message": "1005: Permission denied",
                "error": "You don't have permission to perform this action",
                "timestamp": "2025-08-24T07:47:24.123456+00:00",
                "endpoint": "/api/v1/admin/users/",
                "method": "POST"
            }
        }
    }
)

ERROR_404_SCHEMA = openapi.Response(
    description="Resource not found",
    examples={
        "application/json": {
            "2001: Booking not found": {
                "statusCode": 404,
                "errorCode": 2001,
                "exceptionType": "NotFoundException",
                "message": "2001: Booking not found",
                "error": "Booking with specified ID does not exist",
                "timestamp": "2025-08-24T07:47:24.123456+00:00",
                "endpoint": "/api/v1/bookings/123/",
                "method": "GET"
            }
        }
    }
)

# ============================================================================
# ГОТОВЫЕ СХЕМЫ ДЛЯ ОТВЕТОВ
# ============================================================================

# User schemas
USER_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'username': openapi.Schema(type=openapi.TYPE_STRING),
        'email': openapi.Schema(type=openapi.TYPE_STRING),
        'first_name': openapi.Schema(type=openapi.TYPE_STRING),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING),
        'role': openapi.Schema(type=openapi.TYPE_STRING),
        'phone': openapi.Schema(type=openapi.TYPE_STRING),
        'email_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'provider_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'profile_photo': openapi.Schema(type=openapi.TYPE_STRING),
        'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'last_login': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

USER_CREATE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'user': USER_RESPONSE_SCHEMA,
        'tokens': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                'access': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    }
)

LOGIN_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'access': openapi.Schema(type=openapi.TYPE_STRING),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
        'user': USER_RESPONSE_SCHEMA
    }
)

# Booking schemas
BOOKING_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'customer': openapi.Schema(type=openapi.TYPE_INTEGER),
        'service': openapi.Schema(type=openapi.TYPE_INTEGER),
        'provider': openapi.Schema(type=openapi.TYPE_INTEGER),
        'location': openapi.Schema(type=openapi.TYPE_STRING),
        'preferred_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        'preferred_time': openapi.Schema(type=openapi.TYPE_STRING),
        'scheduled_datetime': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'notes': openapi.Schema(type=openapi.TYPE_STRING),
        'total_price': openapi.Schema(type=openapi.TYPE_NUMBER),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

INTERVIEW_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'customer': openapi.Schema(type=openapi.TYPE_INTEGER),
        'provider': openapi.Schema(type=openapi.TYPE_INTEGER),
        'service': openapi.Schema(type=openapi.TYPE_INTEGER),
        'preferred_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        'preferred_time': openapi.Schema(type=openapi.TYPE_STRING),
        'scheduled_datetime': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'notes': openapi.Schema(type=openapi.TYPE_STRING),
        'admin_notes': openapi.Schema(type=openapi.TYPE_STRING),
        'google_calendar_event_id': openapi.Schema(type=openapi.TYPE_STRING),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

# Service schemas
SERVICE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'title': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'price': openapi.Schema(type=openapi.TYPE_NUMBER),
        'provider': openapi.Schema(type=openapi.TYPE_INTEGER),
        'provider_name': openapi.Schema(type=openapi.TYPE_STRING),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

SCHEDULE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'service': openapi.Schema(type=openapi.TYPE_INTEGER),
        'service_title': openapi.Schema(type=openapi.TYPE_STRING),
        'provider': openapi.Schema(type=openapi.TYPE_INTEGER),
        'provider_name': openapi.Schema(type=openapi.TYPE_STRING),
        'service_provider_name': openapi.Schema(type=openapi.TYPE_STRING),
        'day_of_week': openapi.Schema(type=openapi.TYPE_INTEGER),
        'day_of_week_display': openapi.Schema(type=openapi.TYPE_STRING),
        'start_time': openapi.Schema(type=openapi.TYPE_STRING),
        'end_time': openapi.Schema(type=openapi.TYPE_STRING),
        'is_available': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

# Payment schemas
PAYMENT_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'booking': openapi.Schema(type=openapi.TYPE_INTEGER),
        'customer': openapi.Schema(type=openapi.TYPE_INTEGER),
        'provider': openapi.Schema(type=openapi.TYPE_INTEGER),
        'service': openapi.Schema(type=openapi.TYPE_INTEGER),
        'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
        'currency': openapi.Schema(type=openapi.TYPE_STRING),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'stripe_payment_intent_id': openapi.Schema(type=openapi.TYPE_STRING),
        'stripe_transfer_id': openapi.Schema(type=openapi.TYPE_STRING),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'completed_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

PAYMENT_CREATE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'booking': openapi.Schema(type=openapi.TYPE_INTEGER),
        'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
        'currency': openapi.Schema(type=openapi.TYPE_STRING),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'stripe_payment_intent_id': openapi.Schema(type=openapi.TYPE_STRING),
        'service_title': openapi.Schema(type=openapi.TYPE_STRING),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

# Document schemas
DOCUMENT_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'title': openapi.Schema(type=openapi.TYPE_STRING),
        'description': openapi.Schema(type=openapi.TYPE_STRING),
        'file': openapi.Schema(type=openapi.TYPE_STRING),
        'file_path': openapi.Schema(type=openapi.TYPE_STRING),
        'file_type': openapi.Schema(type=openapi.TYPE_STRING),
        'file_size': openapi.Schema(type=openapi.TYPE_INTEGER),
        'file_extension': openapi.Schema(type=openapi.TYPE_STRING),
        'uploaded_by': openapi.Schema(type=openapi.TYPE_INTEGER),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

# Withdrawal schemas
WITHDRAWAL_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'user': openapi.Schema(type=openapi.TYPE_INTEGER),
        'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
        'currency': openapi.Schema(type=openapi.TYPE_STRING),
        'status': openapi.Schema(type=openapi.TYPE_STRING),
        'stripe_transfer_id': openapi.Schema(type=openapi.TYPE_STRING),
        'reason': openapi.Schema(type=openapi.TYPE_STRING),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'completed_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

# Notification schemas
NOTIFICATION_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'user': openapi.Schema(type=openapi.TYPE_INTEGER),
        'notification_type': openapi.Schema(type=openapi.TYPE_STRING),
        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
        'is_read': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

# Chat schemas
CHAT_ROOM_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'name': openapi.Schema(type=openapi.TYPE_STRING),
        'participants_count': openapi.Schema(type=openapi.TYPE_INTEGER),
        'is_private': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'last_message': openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'content': openapi.Schema(type=openapi.TYPE_STRING),
                'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
            }
        )
    }
)

MESSAGE_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'content': openapi.Schema(type=openapi.TYPE_STRING),
        'sender_username': openapi.Schema(type=openapi.TYPE_STRING),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'is_deleted': openapi.Schema(type=openapi.TYPE_BOOLEAN)
    }
)

# Dashboard schemas
CUSTOMER_DASHBOARD_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'user': openapi.Schema(type=openapi.TYPE_INTEGER),
        'preferred_services': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
        'booking_history_count': openapi.Schema(type=openapi.TYPE_INTEGER),
        'total_spent': openapi.Schema(type=openapi.TYPE_NUMBER),
        'favorite_providers': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
        'notification_preferences': openapi.Schema(type=openapi.TYPE_OBJECT),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

PROVIDER_DASHBOARD_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'user': openapi.Schema(type=openapi.TYPE_INTEGER),
        'calendar_view_type': openapi.Schema(type=openapi.TYPE_STRING),
        'working_hours_start': openapi.Schema(type=openapi.TYPE_STRING),
        'working_hours_end': openapi.Schema(type=openapi.TYPE_STRING),
        'commission_rate': openapi.Schema(type=openapi.TYPE_NUMBER),
        'email_notifications': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'sms_notifications': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'vacation_mode': openapi.Schema(type=openapi.TYPE_BOOLEAN),
        'vacation_start': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        'vacation_end': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        'total_earnings': openapi.Schema(type=openapi.TYPE_NUMBER),
        'total_bookings': openapi.Schema(type=openapi.TYPE_INTEGER),
        'average_rating': openapi.Schema(type=openapi.TYPE_NUMBER),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

MANAGEMENT_DASHBOARD_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        'user': openapi.Schema(type=openapi.TYPE_INTEGER),
        'total_customers_managed': openapi.Schema(type=openapi.TYPE_INTEGER),
        'total_issues_resolved': openapi.Schema(type=openapi.TYPE_INTEGER),
        'total_issues_pending': openapi.Schema(type=openapi.TYPE_INTEGER),
        'total_revenue_managed': openapi.Schema(type=openapi.TYPE_NUMBER),
        'total_providers_managed': openapi.Schema(type=openapi.TYPE_INTEGER),
        'system_health_status': openapi.Schema(type=openapi.TYPE_STRING),
        'last_maintenance_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
    }
)

# ============================================================================
# УПРОЩЕННЫЕ ДЕКОРАТОРЫ ДЛЯ SWAGGER
# ============================================================================

def swagger_auto_schema_simple(
    operation_description,
    request_body=None,
    responses=None,
    tags=None,
    operation_id=None
):
    """
    Упрощенный декоратор для Swagger документации
    """
    if responses is None:
        responses = {
            200: openapi.Response(description="Success"),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        }
    
    return swagger_auto_schema(
        operation_description=operation_description,
        request_body=request_body,
        responses=responses,
        tags=tags,
        operation_id=operation_id
    )

# Готовые декораторы для разных типов операций
def swagger_list_create(description, response_schema, tags=None):
    """Декоратор для ListCreateAPIView"""
    return swagger_auto_schema_simple(
        operation_description=description,
        responses={
            200: openapi.Response(
                description="List retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=response_schema
                )
            ),
            201: openapi.Response(
                description="Created successfully",
                schema=response_schema
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA
        },
        tags=tags
    )

def swagger_retrieve_update_destroy(description, response_schema, tags=None):
    """Декоратор для RetrieveUpdateDestroyAPIView"""
    return swagger_auto_schema_simple(
        operation_description=description,
        responses={
            200: openapi.Response(
                description="Success",
                schema=response_schema
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        },
        tags=tags
    )

def swagger_retrieve_update(description, response_schema, tags=None):
    """Декоратор для RetrieveUpdateAPIView"""
    return swagger_auto_schema_simple(
        operation_description=description,
        responses={
            200: openapi.Response(
                description="Success",
                schema=response_schema
            ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA,
            404: ERROR_404_SCHEMA
        },
        tags=tags
    )

# ============================================================================
# СПИСОК ВСЕХ СХЕМ ДЛЯ ИМПОРТА
# ============================================================================

__all__ = [
    # Error schemas
    'ERROR_400_SCHEMA',
    'ERROR_401_SCHEMA', 
    'ERROR_403_SCHEMA',
    'ERROR_404_SCHEMA',
    
    # User schemas
    'USER_RESPONSE_SCHEMA',
    'USER_CREATE_RESPONSE_SCHEMA',
    'LOGIN_RESPONSE_SCHEMA',
    
    # Booking schemas
    'BOOKING_RESPONSE_SCHEMA',
    'INTERVIEW_RESPONSE_SCHEMA',
    
    # Service schemas
    'SERVICE_RESPONSE_SCHEMA',
    'SCHEDULE_RESPONSE_SCHEMA',
    
    # Payment schemas
    'PAYMENT_RESPONSE_SCHEMA',
    'PAYMENT_CREATE_RESPONSE_SCHEMA',
    
    # Document schemas
    'DOCUMENT_RESPONSE_SCHEMA',
    
    # Withdrawal schemas
    'WITHDRAWAL_RESPONSE_SCHEMA',
    
    # Notification schemas
    'NOTIFICATION_RESPONSE_SCHEMA',
    
    # Chat schemas
    'CHAT_ROOM_RESPONSE_SCHEMA',
    'MESSAGE_RESPONSE_SCHEMA',
    
    # Dashboard schemas
    'CUSTOMER_DASHBOARD_RESPONSE_SCHEMA',
    'PROVIDER_DASHBOARD_RESPONSE_SCHEMA',
    'MANAGEMENT_DASHBOARD_RESPONSE_SCHEMA',
    
    # Utility functions
    'swagger_auto_schema_simple',
    'swagger_list_create',
    'swagger_retrieve_update_destroy',
    'swagger_retrieve_update'
] 
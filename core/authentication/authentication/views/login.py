from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.db import transaction
import logging

from core.error_handling.views import BaseAPIView
from core.error_handling.enums import ErrorCode
from .serializers import CustomTokenObtainPairSerializer
from .models import User

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token acquisition"""
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    """Custom token refresh"""
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Refresh access token using refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            },
            example={
                'refresh': 'your-refresh-token-here'
            }
        ),
        responses={
            200: openapi.Response('Token refreshed successfully', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='New access token'),
                }
            )),
            401: 'Invalid refresh token'
        },
        tags=['Login'])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CustomerLoginView(TokenObtainPairView):
    """Customer login"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Customer authentication (customer)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'fcm_token': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase Cloud Messaging token (optional)'),
            },
            example={
                'email': 'shilovscky@i.ua',
                'password': 'shilovscky',
                'fcm_token': 'your-fcm-token-here'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Customer login with role validation"""
        try:
            email = request.data.get('email')
            fcm_token = request.data.get('fcm_token')
            logger.info(f"Customer login attempt for email: {email}")
            
            if fcm_token:
                logger.info(f"FCM token provided for customer login: {email}")
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Validate user role
                try:
                    user = User.objects.get(email=email)
                    if user.role != 'customer':
                        logger.warning(f"Role mismatch for customer login: {email}, role: {user.role}")
                        return self.error_response(
                            ErrorCode.USER_DELETED,
                            'Invalid role for customer login'
                        )
                    logger.info(f"Customer login successful: {email}")
                    return self.success_response(
                        data=response.data,
                        message='Customer login successful'
                    )
                except User.DoesNotExist:
                    logger.warning(f"Customer login failed - user not found: {email}")
                    return self.error_response(
                        ErrorCode.USER_DELETED,
                        'User not found'
                    )
            else:
                logger.warning(f"Customer login failed for email: {email}")
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Invalid credentials'
                )
                
        except User.DoesNotExist:
            logger.warning(f"Customer login failed - user not found: {request.data.get('email')}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                'User not found'
            )
        except Exception as e:
            logger.error(f"Customer login error: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Login error: {str(e)}'
            )

class ProviderLoginView(TokenObtainPairView):
    """Provider login"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Provider authentication (provider)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'fcm_token': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase Cloud Messaging token (optional)'),
            },
            example={
                'email': 'shilovscky2020@gmail.com',
                'password': 'shilovscky2020',
                'fcm_token': 'your-fcm-token-here'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Provider login with role validation"""
        try:
            email = request.data.get('email')
            fcm_token = request.data.get('fcm_token')
            logger.info(f"Provider login attempt for email: {email}")
            
            if fcm_token:
                logger.info(f"FCM token provided for provider login: {email}")
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Validate user role
                try:
                    user = User.objects.get(email=email)
                    if user.role != 'provider':
                        logger.warning(f"Role mismatch for provider login: {email}, role: {user.role}")
                        return self.error_response(
                            ErrorCode.USER_DELETED,
                            'Invalid role for provider login'
                        )
                    logger.info(f"Provider login successful: {email}")
                    return self.success_response(
                        data=response.data,
                        message='Provider login successful'
                    )
                except User.DoesNotExist:
                    logger.warning(f"Provider login failed - user not found: {email}")
                    return self.error_response(
                        ErrorCode.USER_DELETED,
                        'User not found'
                    )
            else:
                logger.warning(f"Provider login failed for email: {email}")
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Invalid credentials'
                )
                
        except User.DoesNotExist:
            logger.warning(f"Provider login failed - user not found: {request.data.get('email')}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                'User not found'
            )
        except Exception as e:
            logger.error(f"Provider login error: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Login error: {str(e)}'
            )

class ManagementLoginView(TokenObtainPairView):
    """Support Manager login - for customer support staff"""
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Support Manager authentication (support staff)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'fcm_token': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase Cloud Messaging token (optional)'),
            },
            example={
                'email': 'cartiuacarti@gmail.com',
                'password': 'cartiuacarti',
                'fcm_token': 'your-fcm-token-here'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Management login with role validation"""
        try:
            email = request.data.get('email')
            fcm_token = request.data.get('fcm_token')
            logger.info(f"Management login attempt for email: {email}")
            
            if fcm_token:
                logger.info(f"FCM token provided for management login: {email}")
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Validate user role
                try:
                    user = User.objects.get(email=email)
                    if user.role != 'management':
                        logger.warning(f"Role mismatch for management login: {email}, role: {user.role}")
                        return self.error_response(
                            ErrorCode.USER_DELETED,
                            'Invalid role for management login'
                        )
                    logger.info(f"Management login successful: {email}")
                    return self.success_response(
                        data=response.data,
                        message='Management login successful'
                    )
                except User.DoesNotExist:
                    logger.warning(f"Management login failed - user not found: {email}")
                    return self.error_response(
                        ErrorCode.USER_DELETED,
                        'User not found'
                    )
            else:
                logger.warning(f"Management login failed for email: {email}")
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Invalid credentials'
                )
                
        except User.DoesNotExist:
            logger.warning(f"Management login failed - user not found: {request.data.get('email')}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                'User not found'
            )
        except Exception as e:
            logger.error(f"Management login error: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Login error: {str(e)}'
            )

class AdminLoginView(TokenObtainPairView):
    """Admin login - only for admin role"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Admin authentication (admin role only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'fcm_token': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase Cloud Messaging token (optional)'),
            },
            example={
                'email': 'admin@banister.com',
                'password': 'password123',
                'fcm_token': 'your-fcm-token-here'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Admin login with role validation"""
        try:
            email = request.data.get('email')
            fcm_token = request.data.get('fcm_token')
            logger.info(f"Admin login attempt for email: {email}")
            
            if fcm_token:
                logger.info(f"FCM token provided for admin login: {email}")
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Validate user role
                try:
                    user = User.objects.get(email=email)
                    if user.role != 'admin':
                        logger.warning(f"Role mismatch for admin login: {email}, role: {user.role}")
                        return self.error_response(
                            ErrorCode.USER_DELETED,
                            'Invalid role for admin login'
                        )
                    logger.info(f"Admin login successful: {email}")
                    return self.success_response(
                        data=response.data,
                        message='Admin login successful'
                    )
                except User.DoesNotExist:
                    logger.warning(f"Admin login failed - user not found: {email}")
                    return self.error_response(
                        ErrorCode.USER_DELETED,
                        'User not found'
                    )
            else:
                logger.warning(f"Admin login failed for email: {email}")
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Invalid credentials'
                )
                
        except User.DoesNotExist:
            logger.warning(f"Admin login failed - user not found: {request.data.get('email')}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                'User not found'
            )
        except Exception as e:
            logger.error(f"Admin login error: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Login error: {str(e)}'
            )

class SuperAdminLoginView(TokenObtainPairView):
    """Super Admin login - only for super_admin role"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Super Admin authentication (super_admin role only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'fcm_token': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase Cloud Messaging token (optional)'),
            },
            example={
                'email': 'superadmin@banister.com',
                'password': 'AdminPass123!',
                'fcm_token': 'your-fcm-token-here'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Super Admin login with role validation"""
        try:
            email = request.data.get('email')
            fcm_token = request.data.get('fcm_token')
            logger.info(f"Super Admin login attempt for email: {email}")
            
            if fcm_token:
                logger.info(f"FCM token provided for super admin login: {email}")
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Validate user role
                try:
                    user = User.objects.get(email=email)
                    if user.role != 'super_admin':
                        logger.warning(f"Role mismatch for super admin login: {email}, role: {user.role}")
                        return self.error_response(
                            ErrorCode.USER_DELETED,
                            'Invalid role for super admin login'
                        )
                    logger.info(f"Super Admin login successful: {email}")
                    return self.success_response(
                        data=response.data,
                        message='Super Admin login successful'
                    )
                except User.DoesNotExist:
                    logger.warning(f"Super Admin login failed - user not found: {email}")
                    return self.error_response(
                        ErrorCode.USER_DELETED,
                        'User not found'
                    )
            else:
                logger.warning(f"Super Admin login failed for email: {email}")
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Invalid credentials'
                )
                
        except User.DoesNotExist:
            logger.warning(f"Super Admin login failed - user not found: {request.data.get('email')}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                'User not found'
            )
        except Exception as e:
            logger.error(f"Super Admin login error: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Login error: {str(e)}'
            )

class AccountantLoginView(TokenObtainPairView):
    """Accountant login - only for accountant role"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    @swagger_auto_schema(
        operation_description="Accountant authentication (accountant role only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'fcm_token': openapi.Schema(type=openapi.TYPE_STRING, description='Firebase Cloud Messaging token (optional)'),
            },
            example={
                'email': 'accountant@banister.com',
                'password': 'password123',
                'fcm_token': 'your-fcm-token-here'
            }
        ),
        responses={
            200: openapi.Response('Successful authentication', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role'),
                }
            )),
            401: 'Authentication error or role mismatch'
        },
        tags=['Login'])
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Accountant login with role validation"""
        try:
            email = request.data.get('email')
            fcm_token = request.data.get('fcm_token')
            logger.info(f"Accountant login attempt for email: {email}")
            
            if fcm_token:
                logger.info(f"FCM token provided for accountant login: {email}")
            
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Validate user role
                try:
                    user = User.objects.get(email=email)
                    if user.role != 'accountant':
                        logger.warning(f"Role mismatch for accountant login: {email}, role: {user.role}")
                        return self.error_response(
                            ErrorCode.USER_DELETED,
                            'Invalid role for accountant login'
                        )
                    logger.info(f"Accountant login successful: {email}")
                    return self.success_response(
                        data=response.data,
                        message='Accountant login successful'
                    )
                except User.DoesNotExist:
                    logger.warning(f"Accountant login failed - user not found: {email}")
                    return self.error_response(
                        ErrorCode.USER_DELETED,
                        'User not found'
                    )
            else:
                logger.warning(f"Accountant login failed for email: {email}")
                return self.error_response(
                    ErrorCode.USER_DELETED,
                    'Invalid credentials'
                )
                
        except User.DoesNotExist:
            logger.warning(f"Accountant login failed - user not found: {request.data.get('email')}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                'User not found'
            )
        except Exception as e:
            logger.error(f"Accountant login error: {str(e)}")
            return self.error_response(
                ErrorCode.USER_DELETED,
                f'Login error: {str(e)}'
            ) 
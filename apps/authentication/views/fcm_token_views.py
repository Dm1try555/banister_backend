from core.base.common_imports import *
from ..models import UserFCMToken
from ..serializers import FCMTokenSerializer
from core.notifications.service import notification_service
import logging

logger = logging.getLogger(__name__)


class FCMTokenRegisterView(BaseAPIView):
    """Register or update user's FCM token"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Register FCM token for push notifications",
        request_body=FCMTokenSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    @transaction.atomic
    def post(self, request):
        serializer = FCMTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        device_type = serializer.validated_data['device_type']
        
        success = notification_service.register_fcm_token(
            user=request.user,
            token=token,
            device_type=device_type
        )
        
        if success:
            return Response({
                'message': 'FCM token registered successfully',
                'success': True
            })
        else:
            raise CustomValidationError(ErrorCode.INTERNAL_SERVER_ERROR)


class FCMTokenUnregisterView(BaseAPIView):
    """Unregister user's FCM token"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Unregister FCM token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['token']
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    @transaction.atomic
    def post(self, request):
        token = request.data.get('token')
        if not token:
            raise CustomValidationError(ErrorCode.MISSING_REQUIRED_FIELD)
        
        success = notification_service.unregister_fcm_token(token)
        
        if success:
            return Response({
                'message': 'FCM token unregistered successfully',
                'success': True
            })
        else:
            raise CustomValidationError(ErrorCode.INTERNAL_SERVER_ERROR)


class FCMTokenListView(BaseAPIView):
    """Get user's FCM tokens"""
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get user's FCM tokens",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'token': openapi.Schema(type=openapi.TYPE_STRING),
                                'device_type': openapi.Schema(type=openapi.TYPE_STRING),
                                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                                'updated_at': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    )
                }
            )
        }
    )
    def get(self, request):
        tokens = UserFCMToken.objects.filter(user=request.user).order_by('-created_at')
        
        token_data = []
        for token in tokens:
            token_data.append({
                'id': token.id,
                'token': token.token[:20] + '...',  # Mask token for security
                'device_type': token.device_type,
                'is_active': token.is_active,
                'created_at': token.created_at.isoformat(),
                'updated_at': token.updated_at.isoformat()
            })
        
        return Response({
            'tokens': token_data
        })
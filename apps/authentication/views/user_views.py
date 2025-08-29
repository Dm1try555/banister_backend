from core.base.common_imports import *
from ..models import User
from ..serializers import UserSerializer, UserUpdateSerializer


class ProfileView(OptimizedRetrieveUpdateView):
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        action_serializers = {
            'GET': UserSerializer,
            'PUT': UserUpdateSerializer,
            'PATCH': UserUpdateSerializer
        }
        return action_serializers.get(self.request.method, self.serializer_class)
    
    @swagger_auto_schema(
        operation_description="Get user profile information",
        responses={
            200: USER_RESPONSE_SCHEMA,
            401: ERROR_401_SCHEMA
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DeleteProfileView(BaseAPIView):
    
    @swagger_auto_schema(
        operation_description="Delete user profile (only own profile)",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            401: ERROR_401_SCHEMA,
            403: ERROR_403_SCHEMA
        }
    )
    @transaction.atomic
    def delete(self, request):
        user = request.user
        user.delete()
        return self.get_success_response(message='Profile deleted successfully')
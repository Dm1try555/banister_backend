from core.base.common_imports import *
from ..models import User
from ..serializers import UserSerializer, UserUpdateSerializer


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
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


class DeleteProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
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
        
        # Delete user profile
        user.delete()
        
        return Response({
            'message': 'Profile deleted successfully'
        }, status=status.HTTP_200_OK)
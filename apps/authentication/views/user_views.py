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
            200: openapi.Schema(
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
             ),
            401: ERROR_401_SCHEMA
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update user profile information",
        request_body=UserUpdateSerializer,
        responses={
            200: openapi.Schema(
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
                     'provider_verified': openapi.Schema(type=openapi.TYPE_STRING),
                     'profile_photo': openapi.Schema(type=openapi.TYPE_STRING),
                     'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME),
                     'last_login': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME)
                 }
             ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update user profile information",
        request_body=UserUpdateSerializer,
        responses={
            200: openapi.Schema(
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
             ),
            400: ERROR_400_SCHEMA,
            401: ERROR_401_SCHEMA
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
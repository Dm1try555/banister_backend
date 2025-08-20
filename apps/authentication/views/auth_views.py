from .base import *


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm password'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, description='User role', enum=['customer', 'service_provider', 'hr', 'supervisor', 'admin', 'super_admin']),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
                'location': openapi.Schema(type=openapi.TYPE_STRING, description='Location'),
            }
        ),
        responses={
            201: openapi.Response(description="User created successfully"),
            400: openapi.Response(description="Bad request")
        }
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Login user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            }
        ),
        responses={
            200: openapi.Response(description="Login successful"),
            400: openapi.Response(description="Invalid credentials")
        }
    )
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            raise AuthenticationError(ErrorCode.MISSING_REQUIRED_FIELD)
        
        user = authenticate(username=username, password=password)
        if user:
            # Создаём JWT токены
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        else:
            raise AuthenticationError(ErrorCode.INVALID_CREDENTIALS)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Refresh access token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
            }
        ),
        responses={
            200: openapi.Response(description="Token refreshed"),
            400: openapi.Response(description="Invalid token")
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            return Response({
                'access': str(token.access_token),
            })
        except Exception as e:
            raise AuthenticationError(ErrorCode.INVALID_TOKEN)


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get user profile",
        responses={
            200: openapi.Response(description="User profile"),
            401: openapi.Response(description="Unauthorized")
        }
    )
    def get_object(self):
        return self.request.user


# Создаем псевдонимы для обратной совместимости
register = RegisterView.as_view()
login = LoginView.as_view()
refresh_token = RefreshTokenView.as_view()
profile = ProfileView.as_view()
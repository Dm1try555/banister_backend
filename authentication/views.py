from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from .firebase_auth import verify_firebase_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User

class RegisterCustomerView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def perform_create(self, serializer):
        serializer.save(role='customer')

class RegisterProviderView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def perform_create(self, serializer):
        serializer.save(role='provider')

class QuickRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, role):
        data = request.data.copy()
        data['role'] = role
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FirebaseAuthView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, provider):
        id_token = request.data.get('id_token')
        decoded_token = verify_firebase_token(id_token)
        
        email = decoded_token.get('email')
        uid = decoded_token.get('uid')
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'role': 'customer' if provider == 'google' else 'provider',
                'password_hash': uid
            }
        )
        if created:
            Profile.objects.create(user=user)
            if user.role == 'provider':
                from providers.models import Provider
                Provider.objects.create(user=user)
        
        token = CustomTokenObtainPairSerializer.get_token(user)
        return Response({
            'access': str(token.access_token),
            'refresh': str(token)
        })

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class PasswordResetView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            # Implement password reset logic (e.g., send email)
            return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Implement logout logic (e.g., blacklist token)
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer, QuickRegisterRequestSerializer, QuickRegisterVerifySerializer
from .firebase_auth import verify_firebase_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import User, VerificationCode
import random
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterCustomerView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def perform_create(self, serializer):
        serializer.save(role='customer')

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data['email'])
        response.data['role'] = user.role
        return response

class RegisterProviderView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def perform_create(self, serializer):
        serializer.save(role='provider')

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data['email'])
        response.data['role'] = user.role
        return response

class RegisterManagementView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        serializer.save(role='management')

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(email=response.data['email'])
        response.data['role'] = user.role
        return response

class FirebaseAuthView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, provider):
        id_token = request.data.get('id_token')
        role = request.data.get('role', 'customer')
        decoded_token = verify_firebase_token(id_token)
        
        email = decoded_token.get('email')
        uid = decoded_token.get('uid')
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'role': role,
                'password_hash': uid
            }
        )
        if created:
            Profile.objects.create(user=user)
            if user.role == 'provider':
                from providers.models import Provider
                Provider.objects.create(user=user)
        # Если пользователь уже есть, роль не меняется
        token = CustomTokenObtainPairSerializer.get_token(user)
        return Response({
            'access': str(token.access_token),
            'refresh': str(token),
            'role': user.role
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

class VerificationCodeSenderMixin:
    """
    Миксин для отправки кода подтверждения по email или телефону.
    """
    serializer_class = None
    user_check_required = False

    def send_code(self, email, phone):
        code = str(random.randint(100000, 999999))
        VerificationCode.objects.create(email=email, phone=phone, code=code)
        # Здесь должна быть отправка email/SMS
        return code

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            if self.user_check_required:
                if not User.objects.filter(email=email) and not User.objects.filter(phone=phone):
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            code = self.send_code(email, phone)
            return Response({'message': 'Verification code sent', 'code': code}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerificationCodeVerifyMixin:
    """
    Миксин для проверки кода подтверждения и выдачи токена.
    """
    serializer_class = None
    create_user_if_not_exists = False

    def verify_code(self, email, phone, code):
        try:
            vcode = VerificationCode.objects.filter(email=email, phone=phone, code=code, is_used=False).latest('created_at')
        except VerificationCode.DoesNotExist:
            return None, Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        vcode.is_used = True
        vcode.save()
        return vcode, None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            code = serializer.validated_data.get('code')
            vcode, error_response = self.verify_code(email, phone, code)
            if error_response:
                return error_response
            if self.create_user_if_not_exists:
                user, created = User.objects.get_or_create(
                    email=email if email else None,
                    phone=phone if phone else None,
                    defaults={
                        'role': 'customer',
                        'password': User.objects.make_random_password()
                    }
                )
            else:
                try:
                    user = User.objects.get(email=email) if email else User.objects.get(phone=phone)
                except User.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': user.role
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuickRegisterRequestView(VerificationCodeSenderMixin, APIView):
    """
    Запросить код для быстрой регистрации.
    """
    permission_classes = [AllowAny]
    serializer_class = QuickRegisterRequestSerializer
    user_check_required = False

class QuickRegisterVerifyView(VerificationCodeVerifyMixin, APIView):
    """
    Проверить код и зарегистрировать пользователя.
    """
    permission_classes = [AllowAny]
    serializer_class = QuickRegisterVerifySerializer
    create_user_if_not_exists = True

class QuickLoginRequestView(VerificationCodeSenderMixin, APIView):
    """
    Запросить код для быстрого входа (только для существующих пользователей).
    """
    permission_classes = [AllowAny]
    serializer_class = QuickRegisterRequestSerializer
    user_check_required = True

class QuickLoginVerifyView(VerificationCodeVerifyMixin, APIView):
    """
    Проверить код и войти (только для существующих пользователей).
    """
    permission_classes = [AllowAny]
    serializer_class = QuickRegisterVerifySerializer
    create_user_if_not_exists = False
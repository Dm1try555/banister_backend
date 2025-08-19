from .base import *


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))


class SendVerificationEmailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Send email verification code",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
            }
        ),
        responses={
            200: openapi.Response(description="Verification code sent"),
            404: openapi.Response(description="User not found")
        }
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            code = generate_verification_code()
            user.email_verification_code = code
            user.save()
            
            send_mail(
                'Email Verification Code',
                f'Your verification code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({'message': 'Verification code sent'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verify email with code",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'code'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
                'code': openapi.Schema(type=openapi.TYPE_STRING, description='Verification code'),
            }
        ),
        responses={
            200: openapi.Response(description="Email verified successfully"),
            400: openapi.Response(description="Invalid code"),
            404: openapi.Response(description="User not found")
        }
    )
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response({'error': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            if user.email_verification_code == code:
                user.email_verified = True
                user.email_verification_code = None
                user.save()
                return Response({'message': 'Email verified successfully'})
            else:
                return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# Псевдонимы для обратной совместимости
send_verification_email = SendVerificationEmailView.as_view()
verify_email = VerifyEmailView.as_view()
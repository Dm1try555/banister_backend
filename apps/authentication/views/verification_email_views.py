from core.base.common_imports import *
from core.utils import generate_verification_code
from ..models import User
from ..serializers import SendVerificationEmailSerializer, VerifyEmailSerializer
from django.template.loader import render_to_string


class SendVerificationEmailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Send verification code to user email",
        request_body=SendVerificationEmailSerializer,
        responses={
            200: openapi.Response(
                description="Verification code sent",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ERROR_400_SCHEMA,
            404: ERROR_404_SCHEMA
        }
    )
    def post(self, request):
        serializer = SendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            if user.email_verified:
                return Response({'error': 'User already verified'}, status=status.HTTP_400_BAD_REQUEST)
            
            code = generate_verification_code()
            user.email_verification_code = code
            user.save()
            
            html_message = render_to_string('authentication/verification_code_email.html', {
                'code': code,
                'expires_in': '10 minutes'
            })
            
            send_mail(
                subject='Email Verification Code - Banister',
                message=f'Your verification code is: {code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({'message': 'Verification code sent'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verify user email with verification code",
        request_body=VerifyEmailSerializer,
        responses={
            200: openapi.Response(
                description="Email verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ERROR_400_SCHEMA,
            404: ERROR_404_SCHEMA
        }
    )
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
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


send_verification_email = SendVerificationEmailView.as_view()
verify_email = VerifyEmailView.as_view() 
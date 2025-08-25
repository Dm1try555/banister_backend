from core.base.common_imports import *
from ..models import User
from ..serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Request password reset link",
        request_body=PasswordResetRequestSerializer,
        responses={
            200: openapi.Response(
                description="Password reset link sent",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: ERROR_404_SCHEMA
        }
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            
            # Form password reset URL
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            html_message = render_to_string('authentication/password_reset_email.html', {
                'reset_url': reset_url,
                'expires_in': '24 hours'
            })
            
            send_mail(
                subject='Password Reset Request - Banister',
                message=f'Click the link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({'message': 'Password reset link sent'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Confirm password reset with token",
        request_body=PasswordResetConfirmSerializer,
        responses={
            200: openapi.Response(
                description="Password reset successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ERROR_400_SCHEMA
        }
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uidb64 = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Password reset successfully'})
            else:
                return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)


password_reset_request = PasswordResetRequestView.as_view()
password_reset_confirm = PasswordResetConfirmView.as_view() 
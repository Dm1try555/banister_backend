from core.base.common_imports import *
from ..models import User, VerificationCode
from ..serializers import SendVerificationEmailSerializer, VerifyEmailSerializer
from core.mail.service import email_service
import logging

logger = logging.getLogger(__name__)


class SendVerificationEmailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Send verification email to user",
        request_body=SendVerificationEmailSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    def post(self, request):
        serializer = SendVerificationEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate and save verification code
            verification_code = VerificationCode.create_code(
                user=user,
                code_type='email_verification',
                expiry_minutes=10
            )
            
            # Send verification email using centralized service
            email_service.send_verification_email(user, verification_code)
            
            return Response({
                'message': 'Verification email sent successfully. Code expires in 10 minutes.'
            })
            
        except User.DoesNotExist:
            raise CustomValidationError(ErrorCode.USER_NOT_FOUND)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verify user email with code",
        request_body=VerifyEmailSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    def post(self, request):
        # Check code length before serializer validation
        code = request.data.get('code', '')
        if code and len(code) != 4:
            raise CustomValidationError(ErrorCode.INVALID_VERIFICATION_CODE)
        
        # Check if code contains only digits
        if code and not code.isdigit():
            raise CustomValidationError(ErrorCode.INVALID_VERIFICATION_CODE)
        
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        try:
            # Get user by email (handled by serializer validation)
            user = User.objects.get(email=email)
            
            # Find and validate verification code
            try:
                verification_code = VerificationCode.objects.get(
                    user=user,
                    code=code,
                    code_type='email_verification',
                    is_used=False
                )
            except VerificationCode.DoesNotExist:
                raise CustomValidationError(ErrorCode.INVALID_VERIFICATION_CODE)
            
            if not verification_code.is_valid():
                raise CustomValidationError(ErrorCode.VERIFICATION_CODE_EXPIRED)
            
            # Mark email as verified and code as used
            user.email_verified = True
            user.save()
            verification_code.mark_as_used()
            
            return Response({
                'message': 'Email verified successfully.'
            })
            
        except CustomValidationError:
            raise
        except Exception as e:
            logger.error(f"Failed to verify email for {email}: {e}")
            raise CustomValidationError(ErrorCode.EMAIL_VERIFICATION_FAILED)


send_verification_email = SendVerificationEmailView.as_view()
verify_email = VerifyEmailView.as_view() 
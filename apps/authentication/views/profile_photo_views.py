from core.base.common_imports import *
from ..models import User
from ..serializers import ProfilePhotoUploadSerializer
from core.minio.client import minio_client


class ProfilePhotoUploadView(BaseAPIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Upload user profile photo",
        request_body=ProfilePhotoUploadSerializer,
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'profile_photo_url': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ),
            400: ERROR_400_SCHEMA
        }
    )
    def post(self, request):
        serializer = ProfilePhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        photo = serializer.validated_data['photo']
        
        try:
            user = request.user
            
            # Remove old photo if exists
            if user.profile_photo:
                old_photo_name = user.profile_photo.name
                user.profile_photo = None
                user.save()
                
                # Delete old file from MinIO
                if old_photo_name:
                    minio_client.delete_file(old_photo_name)
            
            # Save new photo
            user.profile_photo = photo
            user.save()
            
            # Get photo URL from MinIO
            photo_url = minio_client.client.presigned_get_object(
                minio_client.bucket_name, 
                user.profile_photo.name
            ) if user.profile_photo else ''
            
            return Response({
                'message': 'Profile photo uploaded successfully',
                'profile_photo_url': photo_url
            })
        except (OSError, IOError) as e:
            ErrorCode.INVALID_DATA.raise_error()
        except Exception as e:
            ErrorCode.INTERNAL_SERVER_ERROR.raise_error()


upload_profile_photo = ProfilePhotoUploadView.as_view()
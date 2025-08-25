from core.base.common_imports import *
from ..models import User
from ..serializers import ProfilePhotoUploadSerializer


class ProfilePhotoUploadView(APIView):
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
                old_photo = user.profile_photo
                user.profile_photo = None
                user.save()
                
                # Delete old file
                if old_photo:
                    old_photo.delete(save=False)
            
            user.profile_photo = photo
            user.save()
            
            # Get photo URL (works with any storage backend)
            if hasattr(user.profile_photo, 'url'):
                photo_url = user.profile_photo.url
            else:
                # If storage doesn't support url(), use filename
                photo_url = user.profile_photo.name if user.profile_photo else ''
            
            return Response({
                'message': 'Profile photo uploaded successfully',
                'profile_photo_url': photo_url
            })
        except (OSError, IOError) as e:
            ErrorCode.INVALID_DATA.raise_error()
        except Exception as e:
            ErrorCode.INTERNAL_SERVER_ERROR.raise_error()


upload_profile_photo = ProfilePhotoUploadView.as_view()
from .base import *
from core.minio.client import minio_client
from django.db import transaction
import uuid

class UploadProfilePhotoView(APIView):
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        if 'photo' not in request.FILES:
            return Response({'error': 'No photo provided'}, status=400)
        
        photo = request.FILES['photo']
        
        if photo.size > 5 * 1024 * 1024:
            return Response({'error': 'File too large'}, status=400)
        
        if not photo.content_type.startswith('image/'):
            return Response({'error': 'Invalid file type'}, status=400)
        
        file_name = f"{request.user.id}_{uuid.uuid4()}.jpg"
        
        if request.user.profile_photo:
            old_file = request.user.profile_photo.split('/')[-1]
            minio_client.delete_file(old_file)
        
        photo_url = minio_client.upload_file(photo, file_name)
        
        if photo_url:
            request.user.profile_photo = photo_url
            request.user.save()
            
            return Response({
                'message': 'Profile photo uploaded successfully',
                'photo_url': photo_url
            })
        
        return Response({'error': 'Upload failed'}, status=500)

upload_profile_photo = UploadProfilePhotoView.as_view()
from django.urls import path
from .views import ProfilePhotoUploadView, ProfilePhotoDetailView, ProfilePhotoDeleteView

urlpatterns = [
    path('profile-photo/upload/', ProfilePhotoUploadView.as_view(), name='profile-photo-upload'),
    path('profile-photo/', ProfilePhotoDetailView.as_view(), name='profile-photo-detail'),
    path('profile-photo/delete/', ProfilePhotoDeleteView.as_view(), name='profile-photo-delete'),
] 
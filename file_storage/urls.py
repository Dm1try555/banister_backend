from django.urls import path
from .views import ProfilePhotoUploadView, ProfilePhotoDetailView, ProfilePhotoDeleteView, QuickProfilePhotoChangeView

urlpatterns = [
    path('profile-photo/upload/', ProfilePhotoUploadView.as_view(), name='profile-photo-upload'),
    path('profile-photo/quick-change/', QuickProfilePhotoChangeView.as_view(), name='profile-photo-quick-change'),
    path('profile-photo/', ProfilePhotoDetailView.as_view(), name='profile-photo-detail'),
    path('profile-photo/delete/', ProfilePhotoDeleteView.as_view(), name='profile-photo-delete'),
] 
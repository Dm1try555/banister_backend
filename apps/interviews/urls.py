from django.urls import path
from .views import (
    InterviewListCreateView, InterviewDetailView,
    InterviewRequestListCreateView, InterviewRequestDetailView,
    TestGoogleMeetView
)

urlpatterns = [
    # Interview URLs
    path('interviews/', InterviewListCreateView.as_view(), name='interview-list-create'),
    path('interviews/<int:pk>/', InterviewDetailView.as_view(), name='interview-detail'),
    
    # Interview Request URLs
    path('interview-requests/', InterviewRequestListCreateView.as_view(), name='interview-request-list-create'),
    path('interview-requests/<int:pk>/', InterviewRequestDetailView.as_view(), name='interview-request-detail'),
    
    # Test Google Meet URL
    path('test-google-meet/', TestGoogleMeetView.as_view(), name='test-google-meet'),
]
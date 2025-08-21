from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet, InterviewViewSet

router = DefaultRouter()
router.register(r'bookings', BookingViewSet)
router.register(r'interviews', InterviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
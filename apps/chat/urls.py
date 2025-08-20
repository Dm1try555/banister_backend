from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')

urlpatterns = [
    path('', include(router.urls)),
    path('rooms/<int:room_id>/messages/', MessageViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='room-messages-list'),
    path('rooms/<int:room_id>/messages/<int:pk>/', MessageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='room-messages-detail'),
]
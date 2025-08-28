from django.urls import path
from .views import (
    ChatRoomListCreateView, ChatRoomDetailView,
    MessageListCreateView, MessageDetailView, MessageListByRoomView
)

urlpatterns = [
    # Chat Room URLs
    path('rooms/', ChatRoomListCreateView.as_view(), name='chatroom-list-create'),
    path('rooms/<int:pk>/', ChatRoomDetailView.as_view(), name='chatroom-detail'),
    
    # Message URLs
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
    path('rooms/<int:room_id>/messages/', MessageListByRoomView.as_view(), name='message-list-by-room'),
]
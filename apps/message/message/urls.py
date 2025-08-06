from django.urls import path
from .views import (
    ChatListView, ChatDetailView, MessageListView, 
    MessageCreateView, MessageDetailView
)

app_name = 'message'

urlpatterns = [
    # Чаты
    path('chats/', ChatListView.as_view(), name='chat-list'),  # GET/POST /api/v1/message/chats/
    path('chats/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),  # GET /api/v1/message/chats/{id}/
    
    # Сообщения
    path('chats/<int:chat_id>/messages/', MessageListView.as_view(), name='message-list'),  # GET /api/v1/message/chats/{chat_id}/messages/
    path('messages/', MessageCreateView.as_view(), name='message-create'),  # POST /api/v1/message/messages/
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),  # GET/PUT/DELETE /api/v1/message/messages/{id}/
]
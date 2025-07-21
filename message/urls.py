from django.urls import path
from .views import ChatListView, ChatDetailView, MessageCreateView, MessageDetailView

urlpatterns = [
    path('', ChatListView.as_view(), name='chat-list'),  # GET /api/v1/message/
    path('', MessageCreateView.as_view(), name='message-create'),  # POST /api/v1/message/
    path('<int:pk>/', MessageDetailView.as_view(), name='message-detail'),  # GET /api/v1/message/{id}/
    path('chat/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),  # GET /api/v1/message/chat/{id}/ (опционально)
]
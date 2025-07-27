from django.urls import path
from .views import MessageListCreateView, MessageDetailView, ChatDetailView

urlpatterns = [
    path('', MessageListCreateView.as_view(), name='message-list-create'),  # GET/POST /api/v1/message/
    path('<int:pk>/', MessageDetailView.as_view(), name='message-detail'),  # GET /api/v1/message/{id}/
    path('chat/<int:pk>/', ChatDetailView.as_view(), name='chat-detail'),  # GET /api/v1/message/chat/{id}/
]
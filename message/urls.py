from django.urls import path
from .views import ChatListView, ChatDetailView, MessageCreateView

urlpatterns = [
    path('', ChatListView.as_view(), name='chat-list'),
    path('<int:pk>', ChatDetailView.as_view(), name='chat-detail'),
    path('', MessageCreateView.as_view(), name='message-create'),
]
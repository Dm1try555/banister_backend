from django.urls import path
from .views import DocumentListView, DocumentCreateView, DocumentDeleteView

urlpatterns = [
    path('', DocumentListView.as_view(), name='document-list'),
    path('create/', DocumentCreateView.as_view(), name='document-create'),
    path('<int:pk>/', DocumentDeleteView.as_view(), name='document-delete'),
] 
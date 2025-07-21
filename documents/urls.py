from django.urls import path
from .views import DocumentListCreateView, DocumentDeleteView

urlpatterns = [
    path('', DocumentListCreateView.as_view(), name='document-list-create'),  # GET/POST /api/v1/documents/
    path('<int:pk>/', DocumentDeleteView.as_view(), name='document-delete'),  # DELETE /api/v1/documents/{id}/
] 
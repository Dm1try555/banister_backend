from core.base.common_imports import *
from .models import Document
from .serializers import (
    DocumentSerializer, DocumentCreateSerializer, DocumentUpdateSerializer,
    DocumentUploadSerializer
)
from .permissions import DocumentPermissions


class DocumentListCreateView(SwaggerMixin, ListCreateAPIView, RoleBasedQuerysetMixin, DocumentPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()

    def get_serializer_class(self):
        return DocumentCreateSerializer if self.request.method == 'POST' else DocumentSerializer

    @swagger_list_create(
        description="Create new document",
        response_schema=DOCUMENT_RESPONSE_SCHEMA,
        tags=["Documents"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class DocumentDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBasedQuerysetMixin, DocumentPermissions):
    permission_classes = [IsAuthenticated]
    queryset = Document.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DocumentUpdateSerializer
        return DocumentSerializer


from core.base.common_imports import *
from core.base.role_base import RoleBase
from .models import Document
from .serializers import (
    DocumentSerializer, DocumentCreateSerializer, DocumentUpdateSerializer,
    DocumentUploadSerializer
)


class DocumentListCreateView(SwaggerMixin, ListCreateAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Document.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Document, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Document, user)
        return self._get_admin_queryset(Document, user)

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


class DocumentDetailView(SwaggerMixin, RetrieveUpdateDestroyAPIView, RoleBase):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Document.objects.none()
            
        user = self.request.user
        if user.role == 'customer':
            return self._get_customer_queryset(Document, user)
        elif user.role == 'service_provider':
            return self._get_service_provider_queryset(Document, user)
        return self._get_admin_queryset(Document, user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DocumentUpdateSerializer
        return DocumentSerializer

    @swagger_retrieve_update_destroy(
        description="Retrieve, update or delete document",
        response_schema=DOCUMENT_RESPONSE_SCHEMA,
        tags=["Documents"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Update document",
        response_schema=DOCUMENT_RESPONSE_SCHEMA,
        tags=["Documents"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Partially update document",
        response_schema=DOCUMENT_RESPONSE_SCHEMA,
        tags=["Documents"]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_retrieve_update_destroy(
        description="Delete document",
        response_schema=openapi.Response(description="Document deleted successfully"),
        tags=["Documents"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
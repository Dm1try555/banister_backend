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
        response_schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        tags=["Documents"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
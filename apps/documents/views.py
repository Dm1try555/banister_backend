from .models import Document
from .serializers import DocumentSerializer
from core.base.views import BaseModelViewSet

class DocumentViewSet(BaseModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
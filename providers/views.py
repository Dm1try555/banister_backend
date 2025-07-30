from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Provider
from .serializers import ProviderSerializer
from error_handling.views import BaseAPIView

class ProviderListView(BaseAPIView, generics.ListAPIView):
    """List of all providers"""
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]

class ProviderDetailView(BaseAPIView, generics.RetrieveAPIView):
    """Detailed provider information"""
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]
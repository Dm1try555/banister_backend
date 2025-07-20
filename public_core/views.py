from rest_framework import generics
from rest_framework.permissions import AllowAny
from services.models import Service
from services.serializers import ServiceSerializer
from providers.models import Provider
from providers.serializers import ProviderSerializer

class PublicServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]

class PublicProviderListView(generics.ListAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]

class PublicProviderDetailView(generics.RetrieveAPIView):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [AllowAny]
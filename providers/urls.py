from django.urls import path
from .views import ProviderListView, ProviderDetailView

urlpatterns = [
    path('providers', ProviderListView.as_view(), name='provider-list'),
    path('providers/<int:pk>', ProviderDetailView.as_view(), name='provider-detail'),
]
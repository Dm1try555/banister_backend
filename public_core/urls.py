# public_core/urls.py
from django.urls import path
from .views import PublicServiceListView, PublicProviderListView, PublicProviderDetailView

urlpatterns = [
    path('services', PublicServiceListView.as_view(), name='public-service-list'),
    path('providers', PublicProviderListView.as_view(), name='public-provider-list'),
    path('providers/<int:pk>', PublicProviderDetailView.as_view(), name='public-provider-detail'),
]
from django.db import transaction
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, 
    RetrieveUpdateAPIView, CreateAPIView
)
from core.base.common_imports import *
from core.base.optimized_views import OptimizedCRUDMixin, OptimizedListMixin, OptimizedDetailMixin


class OptimizedListCreateView(SwaggerMixin, OptimizedListMixin, ListCreateAPIView):
    """Optimized base view for list and create operations"""
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class OptimizedRetrieveUpdateDestroyView(SwaggerMixin, OptimizedCRUDMixin, OptimizedDetailMixin, RetrieveUpdateDestroyAPIView):
    """Optimized base view for retrieve, update, and destroy operations"""
    pass


class OptimizedRetrieveUpdateView(SwaggerMixin, OptimizedCRUDMixin, OptimizedDetailMixin, RetrieveUpdateAPIView):
    """Optimized base view for retrieve and update operations"""
    pass


class OptimizedCreateView(SwaggerMixin, CreateAPIView):
    """Optimized base view for create operations"""
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class OptimizedModelViewSet(SwaggerMixin, OptimizedCRUDMixin, OptimizedListMixin, OptimizedDetailMixin, ModelViewSet):
    """Optimized base viewset for all CRUD operations"""
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
from django.urls import path
from .views import ServiceListView, ServiceDetailView

urlpatterns = [
    path('', ServiceListView.as_view(), name='service-list'),  # GET /api/v1/services/
    path('<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),  # GET /api/v1/services/{id}/
]
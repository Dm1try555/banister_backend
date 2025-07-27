from django.urls import path
from .views import PaymentListCreateView, PaymentStatusView

urlpatterns = [
    path('', PaymentListCreateView.as_view(), name='payment-list-create'),  # GET/POST /api/v1/payments/
    path('<int:pk>/', PaymentStatusView.as_view(), name='payment-status'),  # GET /api/v1/payments/{id}/
]
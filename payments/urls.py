from django.urls import path
from .views import PaymentHistoryView, PaymentInitiateView, PaymentStatusView

urlpatterns = [
    path('', PaymentHistoryView.as_view(), name='payment-history'),  # GET /api/v1/payments/
    path('', PaymentInitiateView.as_view(), name='payment-initiate'),  # POST /api/v1/payments/
    path('<int:pk>/', PaymentStatusView.as_view(), name='payment-status'),  # GET /api/v1/payments/{id}/
]
from django.urls import path
from .views import (
    PaymentListCreateView, PaymentDetailView,
    PaymentConfirmView, PaymentTransferView
)

urlpatterns = [
    # Payment URLs
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:pk>/', PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/confirm/', PaymentConfirmView.as_view(), name='payment-confirm'),
    path('payments/transfer/', PaymentTransferView.as_view(), name='payment-transfer'),
]
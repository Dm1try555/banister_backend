from django.urls import path
from .views import PaymentInitiateView, PaymentStatusView, PaymentHistoryView

urlpatterns = [
    path('initiate', PaymentInitiateView.as_view(), name='payment-initiate'),
    path('status/<int:pk>', PaymentStatusView.as_view(), name='payment-status'),
    path('history', PaymentHistoryView.as_view(), name='payment-history'),
]
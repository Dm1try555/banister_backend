from django.urls import path
from .views import (
    PaymentListCreateView, PaymentStatusView,
    StripeCreatePaymentIntentView, StripeConfirmPaymentView,
    StripeCreateCustomerView, StripeAttachPaymentMethodView,
    StripePaymentStatusView, StripeRefundPaymentView
)

urlpatterns = [
    # Основные операции с платежами
    path('', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('<int:pk>/', PaymentStatusView.as_view(), name='payment-status'),
    
    # Stripe интеграция
    path('stripe/create-intent/', StripeCreatePaymentIntentView.as_view(), name='stripe-create-intent'),
    path('stripe/confirm-payment/', StripeConfirmPaymentView.as_view(), name='stripe-confirm-payment'),
    path('stripe/create-customer/', StripeCreateCustomerView.as_view(), name='stripe-create-customer'),
    path('stripe/attach-payment-method/', StripeAttachPaymentMethodView.as_view(), name='stripe-attach-payment-method'),
    path('stripe/payment-status/', StripePaymentStatusView.as_view(), name='stripe-payment-status'),
    path('stripe/refund/', StripeRefundPaymentView.as_view(), name='stripe-refund'),
]
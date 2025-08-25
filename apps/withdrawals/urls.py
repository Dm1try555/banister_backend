from django.urls import path
from .views import (
    WithdrawalListCreateView, WithdrawalDetailView,
    WithdrawalApproveView, WithdrawalRejectView
)

urlpatterns = [
    # Withdrawal URLs
    path('withdrawals/', WithdrawalListCreateView.as_view(), name='withdrawal-list-create'),
    path('withdrawals/<int:pk>/', WithdrawalDetailView.as_view(), name='withdrawal-detail'),
    path('withdrawals/<int:pk>/approve/', WithdrawalApproveView.as_view(), name='withdrawal-approve'),
    path('withdrawals/<int:pk>/reject/', WithdrawalRejectView.as_view(), name='withdrawal-reject'),
]
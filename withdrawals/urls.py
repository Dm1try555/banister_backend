from django.urls import path
from .views import WithdrawalHistoryView, WithdrawalCreateView

urlpatterns = [
    path('', WithdrawalHistoryView.as_view(), name='withdrawal-history'),  # GET /api/v1/withdrawals/
    path('', WithdrawalCreateView.as_view(), name='withdrawal-create'),  # POST /api/v1/withdrawals/
]
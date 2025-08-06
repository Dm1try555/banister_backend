from django.urls import path
from .views import WithdrawalListCreateView

urlpatterns = [
    path('', WithdrawalListCreateView.as_view(), name='withdrawal-list-create'),  # GET/POST /api/v1/withdrawals/
]
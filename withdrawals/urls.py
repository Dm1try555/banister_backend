from django.urls import path
from .views import WithdrawalCreateView, WithdrawalHistoryView

urlpatterns = [
    path('', WithdrawalCreateView.as_view(), name='withdrawal-create'),
    path('', WithdrawalHistoryView.as_view(), name='withdrawal-history'),
]
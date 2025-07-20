from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Withdrawal
from .serializers import WithdrawalSerializer

class WithdrawalCreateView(generics.CreateAPIView):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(provider=self.request.user)

class WithdrawalHistoryView(generics.ListAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Withdrawal.objects.filter(provider=self.request.user)
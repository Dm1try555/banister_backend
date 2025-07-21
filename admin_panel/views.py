from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import AdminIssue
from .serializers import AdminIssueSerializer
from authentication.models import User
from authentication.serializers import UserSerializer

class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class AdminUserDetailView(generics.RetrieveDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class AdminIssueListView(generics.ListAPIView):
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

class AdminIssueCreateView(generics.CreateAPIView):
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

class AdminIssueDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdminIssue.objects.all()
    serializer_class = AdminIssueSerializer
    permission_classes = [IsAdminUser]

class CustomerListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    def get_queryset(self):
        return User.objects.filter(role='customer')

class ProviderListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    def get_queryset(self):
        return User.objects.filter(role='provider')
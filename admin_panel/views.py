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

class AdminIssueResolveView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request, pk):
        try:
            issue = AdminIssue.objects.get(pk=pk)
            issue.status = 'resolved'
            issue.save()
            return Response(AdminIssueSerializer(issue).data)
        except AdminIssue.DoesNotExist:
            return Response({'error': 'Issue not found'}, status=404)
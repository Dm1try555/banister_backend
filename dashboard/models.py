from django.db import models
from authentication.models import User

class DashboardStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_stats')
    total_bookings = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
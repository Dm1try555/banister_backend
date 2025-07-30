from django.db import models
from authentication.models import User

class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider')
    verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    experience_years = models.IntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)






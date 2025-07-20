from django.db import models
from authentication.models import User

class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider')
    verified = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)




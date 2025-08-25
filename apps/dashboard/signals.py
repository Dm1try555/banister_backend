from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import CustomerDashboard, ProviderDashboard, ManagementDashboard

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_dashboard(sender, instance, created, **kwargs):
    """Create dashboard for new user"""
    if created:
        # Remove old dashboards
        CustomerDashboard.objects.filter(user=instance).delete()
        ProviderDashboard.objects.filter(user=instance).delete()
        ManagementDashboard.objects.filter(user=instance).delete()
        
        # Create new dashboard based on user role
        if instance.role == 'customer':
            CustomerDashboard.objects.create(user=instance)
        elif instance.role == 'service_provider':
            ProviderDashboard.objects.create(user=instance)
        elif instance.is_staff:
            ManagementDashboard.objects.create(user=instance) 
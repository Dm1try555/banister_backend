from .models import Service, Schedule
from .serializers import ServiceSerializer, ServiceCreateSerializer, ScheduleSerializer
from core.base.views import ServiceProviderViewSet, AdminViewSet

class ServiceViewSet(ServiceProviderViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    pagination_class = None
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ServiceCreateSerializer
        return super().get_serializer_class()

class ScheduleViewSet(AdminViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, ScheduleViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'schedules', ScheduleViewSet)
urlpatterns = router.urls
from rest_framework.routers import DefaultRouter
from .views import CustomerDashboardViewSet, ProviderDashboardViewSet, ManagementDashboardViewSet, IssueViewSet

router = DefaultRouter()
router.register(r'customer-dashboard', CustomerDashboardViewSet)
router.register(r'provider-dashboard', ProviderDashboardViewSet)
router.register(r'management-dashboard', ManagementDashboardViewSet)
router.register(r'issues', IssueViewSet)
urlpatterns = router.urls
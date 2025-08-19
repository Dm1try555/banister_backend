from rest_framework.routers import DefaultRouter
from .views import WithdrawalViewSet

router = DefaultRouter()
router.register(r'withdrawals', WithdrawalViewSet)
urlpatterns = router.urls
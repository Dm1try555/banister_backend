from django.urls import path
from .views import ErrorTestView

app_name = 'error_handling'

urlpatterns = [
    path('test/', ErrorTestView.as_view(), name='error_test'),
] 
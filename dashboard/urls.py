from django.urls import path
from .views import DashboardViewSet

urlpatterns = [
    path('dashboard/get_stats/',DashboardViewSet.as_view({'get':'get_stats'}),name='get_stats')
]

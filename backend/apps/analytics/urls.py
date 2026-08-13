from django.urls import path
from .views import AnalyticsOverviewView, DepartmentAnalyticsView

urlpatterns = [
    path('overview/', AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('departments/', DepartmentAnalyticsView.as_view(), name='analytics-departments'),
]

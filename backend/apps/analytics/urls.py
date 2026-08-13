from django.urls import path
from .views import AnalyticsOverviewView, DepartmentAnalyticsView, CompanyAnalyticsView

urlpatterns = [
    path('overview/', AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('departments/', DepartmentAnalyticsView.as_view(), name='analytics-departments'),
    path('companies/', CompanyAnalyticsView.as_view(), name='analytics-companies'),
]

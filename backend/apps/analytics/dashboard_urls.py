from django.urls import path
from .views import DashboardSummaryView, RecentActivityView, PackageStatisticsView, DriveStatisticsView, StudentDashboardSummaryView

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('student-summary/', StudentDashboardSummaryView.as_view(), name='student-dashboard-summary'),
    path('recent-activity/', RecentActivityView.as_view(), name='dashboard-recent-activity'),
    path('package-statistics/', PackageStatisticsView.as_view(), name='dashboard-package-statistics'),
    path('drive-statistics/', DriveStatisticsView.as_view(), name='dashboard-drive-statistics'),
]

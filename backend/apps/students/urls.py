from django.urls import path
from .views import (
    StudentCreateAPIView,
    StudentProfileAPIView,
    StudentProfileUpdateAPIView,
    StudentListAPIView
)

app_name = 'students'

urlpatterns = [
    path('create/', StudentCreateAPIView.as_view(), name='student-create'),
    path('profile/', StudentProfileAPIView.as_view(), name='student-profile'),
    path('profile/update/', StudentProfileUpdateAPIView.as_view(), name='student-profile-update'),
    path('list/', StudentListAPIView.as_view(), name='student-list'),
]

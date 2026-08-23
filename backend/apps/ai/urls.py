from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CareerRecommendationViewSet, RecommendedDrivesView

router = DefaultRouter()
router.register(r'recommendations', CareerRecommendationViewSet, basename='career-recommendation')

urlpatterns = [
    path('recommended-drives/', RecommendedDrivesView.as_view(), name='recommended-drives'),
    path('', include(router.urls)),
]

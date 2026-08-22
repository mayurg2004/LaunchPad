from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CareerRecommendationViewSet

router = DefaultRouter()
router.register(r'recommendations', CareerRecommendationViewSet, basename='career-recommendation')

urlpatterns = [
    path('', include(router.urls)),
]

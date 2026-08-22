from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import CareerRecommendation
from .serializers import CareerRecommendationSerializer
from accounts.models import UserRole

class CareerRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CareerRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role in [UserRole.ADMIN, UserRole.PLACEMENT_OFFICER]:
            return CareerRecommendation.objects.all()
        elif user.role == UserRole.STUDENT:
            return CareerRecommendation.objects.filter(student__user=user)
        return CareerRecommendation.objects.none()


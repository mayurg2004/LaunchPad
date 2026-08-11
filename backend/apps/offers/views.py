from rest_framework import viewsets
from .models import Offer
from .serializers import OfferSerializer
from .permissions import OfferPermissions
from accounts.models import UserRole

class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [OfferPermissions]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        
        if user.is_anonymous:
            return Offer.objects.none()
            
        if user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            return Offer.objects.all()
            
        if user.role == UserRole.STUDENT and hasattr(user, 'student_profile'):
            return Offer.objects.filter(student=user.student_profile)
            
        return Offer.objects.none()

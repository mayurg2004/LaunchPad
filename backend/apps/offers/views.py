from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Offer
from .serializers import OfferSerializer, RespondOfferSerializer
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

    @action(detail=True, methods=['patch'])
    def respond(self, request, pk=None):
        offer = self.get_object()
        serializer = RespondOfferSerializer(data=request.data, context={'offer': offer})
        
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            offer.status = new_status
            offer.save()
            
            if new_status == 'ACCEPTED':
                student = offer.student
                student.is_placed = True
                student.save()
                
                application = offer.application
                application.status = 'SELECTED'
                application.save()
                
            return Response({'status': f'Offer {new_status}'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

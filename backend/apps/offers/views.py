from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from .models import Offer
from .serializers import OfferSerializer, RespondOfferSerializer
from .permissions import OfferPermissions
from accounts.models import UserRole

class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [OfferPermissions]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']
    filter_backends = [OrderingFilter]
    ordering_fields = ['offer_date', 'package_lpa', 'joining_date']

    def get_queryset(self):
        user = self.request.user
        
        if user.is_anonymous:
            return Offer.objects.none()
            
        if user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            return Offer.objects.all()
            
        if user.role == UserRole.STUDENT and hasattr(user, 'student_profile'):
            return Offer.objects.filter(student=user.student_profile)
            
        return Offer.objects.none()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        
        company = self.request.query_params.get('company')
        if company:
            queryset = queryset.filter(company_id=company)
            
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        offer_type = self.request.query_params.get('offer_type')
        if offer_type:
            queryset = queryset.filter(offer_type=offer_type)
            
        placement_drive = self.request.query_params.get('placement_drive')
        if placement_drive:
            queryset = queryset.filter(placement_drive_id=placement_drive)
            
        return queryset

    @action(detail=False, methods=['get'], url_path='my-offers')
    def my_offers(self, request):
        if request.user.role != UserRole.STUDENT or not hasattr(request.user, 'student_profile'):
            return Response({"error": "Only students can view their offers"}, status=status.HTTP_403_FORBIDDEN)
            
        queryset = Offer.objects.filter(student=request.user.student_profile)
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def accepted(self, request):
        if request.user.role not in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
            
        queryset = Offer.objects.filter(status='ACCEPTED')
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='placement-status')
    def placement_status(self, request):
        if request.user.role != UserRole.STUDENT or not hasattr(request.user, 'student_profile'):
            return Response({"error": "Only students can access this endpoint"}, status=status.HTTP_403_FORBIDDEN)
            
        student = request.user.student_profile
        offers = Offer.objects.filter(student=student)
        
        return Response({
            'is_placed': student.is_placed,
            'total_offers': offers.count(),
            'accepted_offers': offers.filter(status='ACCEPTED').count(),
            'rejected_offers': offers.filter(status='REJECTED').count()
        }, status=status.HTTP_200_OK)

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

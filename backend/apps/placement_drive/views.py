from rest_framework import viewsets, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .models import PlacementDrive
from .serializers import PlacementDriveSerializer

class PlacementDrivePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PlacementDriveViewSet(viewsets.ModelViewSet):
    queryset = PlacementDrive.objects.all().order_by('-created_at')
    serializer_class = PlacementDriveSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'job_role', 'company__company_name']
    ordering_fields = ['application_deadline', 'package_lpa', 'created_at']
    pagination_class = PlacementDrivePagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        company = self.request.query_params.get('company')
        status = self.request.query_params.get('status')
        minimum_cgpa = self.request.query_params.get('minimum_cgpa')
        
        if company:
            queryset = queryset.filter(company_id=company)
        if status:
            queryset = queryset.filter(status=status)
        if minimum_cgpa:
            queryset = queryset.filter(minimum_cgpa=minimum_cgpa)
            
        return queryset

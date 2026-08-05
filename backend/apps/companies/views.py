from rest_framework import viewsets, filters
from .models import Company
from .serializers import CompanySerializer
from .permissions import IsPlacementOfficerOrAdminOrReadOnly

class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsPlacementOfficerOrAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name']
    ordering_fields = ['company_name', 'created_at']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        queryset = Company.objects.all()
        industry = self.request.query_params.get('industry')
        company_type = self.request.query_params.get('company_type')

        if industry:
            queryset = queryset.filter(industry__iexact=industry)
        if company_type:
            queryset = queryset.filter(company_type__iexact=company_type)

        return queryset

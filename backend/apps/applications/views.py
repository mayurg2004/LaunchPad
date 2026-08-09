from rest_framework import viewsets, mixins, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Application
from .serializers import (
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer
)
from .permissions import ApplicationPermissions
from accounts.models import UserRole

class ApplicationViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `list()` actions.
    Updates are restricted to the custom `status` action.
    """
    permission_classes = [ApplicationPermissions]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__enrollment_number', 'placement_drive__company__company_name', 'placement_drive__title']
    ordering_fields = ['applied_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ApplicationCreateSerializer
        elif self.action == 'status':
            return ApplicationStatusUpdateSerializer
        return ApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Application.objects.all().order_by('-applied_at')

        if not user.is_authenticated:
            return Application.objects.none()

        # Role-based filtering
        if user.role == UserRole.STUDENT:
            if hasattr(user, 'student_profile'):
                queryset = queryset.filter(student=user.student_profile)
            else:
                queryset = Application.objects.none()
        elif user.role == UserRole.RECRUITER:
            if hasattr(user, 'recruiter_profile') and hasattr(user.recruiter_profile, 'company'):
                queryset = queryset.filter(placement_drive__company=user.recruiter_profile.company)
            else:
                queryset = Application.objects.none()
        elif user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            # They see all applications
            pass

        # Query param filtering
        placement_drive = self.request.query_params.get('placement_drive')
        company = self.request.query_params.get('company')
        app_status = self.request.query_params.get('status')
        student = self.request.query_params.get('student')

        if placement_drive:
            queryset = queryset.filter(placement_drive_id=placement_drive)
        if company:
            queryset = queryset.filter(placement_drive__company_id=company)
        if app_status:
            queryset = queryset.filter(status=app_status)
        if student:
            queryset = queryset.filter(student_id=student)

        return queryset

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        application = self.get_object()
        
        # Only Placement Officers and Admins can update status (checked by permissions, but extra safety check)
        if request.user.role not in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            return Response({'error': 'You do not have permission to update the status.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(application, data=request.data, partial=True)
        if serializer.is_valid():
            # Basic status transition logic could be added here if needed in the future
            valid_statuses = [choice[0] for choice in Application.APPLICATION_STATUS_CHOICES]
            if serializer.validated_data.get('status') not in valid_statuses:
                 return Response({'error': 'Invalid status provided.'}, status=status.HTTP_400_BAD_REQUEST)
                 
            serializer.save()
            # Return full application details after update
            return Response(ApplicationSerializer(application).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='my-applications')
    def my_applications(self, request):
        if request.user.role != UserRole.STUDENT or not hasattr(request.user, 'student_profile'):
            return Response({'error': 'Only students can view their applications.'}, status=status.HTTP_403_FORBIDDEN)
            
        queryset = Application.objects.filter(student=request.user.student_profile).order_by('-applied_at')
        
        # Optional: apply pagination manually or let DRF handle if page query param exists
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ApplicationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ApplicationSerializer(queryset, many=True)
        return Response(serializer.data)

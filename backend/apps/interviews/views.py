from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Interview
from .serializers import (
    InterviewSerializer, 
    InterviewStatusUpdateSerializer,
    InterviewResultUpdateSerializer
)
from .permissions import InterviewPermissions
from accounts.models import UserRole

class InterviewViewSet(viewsets.ModelViewSet):
    permission_classes = [InterviewPermissions]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['scheduled_at', 'created_at']

    def get_serializer_class(self):
        if self.action == 'status':
            return InterviewStatusUpdateSerializer
        if self.action == 'result':
            return InterviewResultUpdateSerializer
        return InterviewSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Interview.objects.all().order_by('scheduled_at')

        if not user.is_authenticated:
            return Interview.objects.none()

        if user.role == UserRole.STUDENT:
            if hasattr(user, 'student_profile'):
                queryset = queryset.filter(application__student=user.student_profile)
            else:
                queryset = Interview.objects.none()
        elif user.role == UserRole.RECRUITER:
            if hasattr(user, 'recruiter_profile') and hasattr(user.recruiter_profile, 'company'):
                queryset = queryset.filter(application__placement_drive__company=user.recruiter_profile.company)
            else:
                queryset = Interview.objects.none()
        elif user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            pass

        # Query param filtering
        round_type = self.request.query_params.get('round_type')
        app_status = self.request.query_params.get('status')
        result = self.request.query_params.get('result')
        application = self.request.query_params.get('application')
        placement_drive = self.request.query_params.get('placement_drive')
        company = self.request.query_params.get('company')

        if round_type:
            queryset = queryset.filter(round_type=round_type)
        if app_status:
            queryset = queryset.filter(status=app_status)
        if result:
            queryset = queryset.filter(result=result)
        if application:
            queryset = queryset.filter(application_id=application)
        if placement_drive:
            queryset = queryset.filter(application__placement_drive_id=placement_drive)
        if company:
            queryset = queryset.filter(application__placement_drive__company_id=company)

        return queryset

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        if request.user.role != UserRole.STUDENT or not hasattr(request.user, 'student_profile'):
            return Response({'error': 'Only students can view their upcoming interviews via this endpoint.'}, status=status.HTTP_403_FORBIDDEN)
            
        queryset = Interview.objects.filter(
            application__student=request.user.student_profile,
            status='SCHEDULED',
            scheduled_at__gt=timezone.now()
        ).order_by('scheduled_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = InterviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = InterviewSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        interview = self.get_object()
        serializer = self.get_serializer(interview, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(InterviewSerializer(interview).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def result(self, request, pk=None):
        interview = self.get_object()
        serializer = self.get_serializer(interview, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(InterviewSerializer(interview).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
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

        return queryset

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

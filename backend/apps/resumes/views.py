from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.models import UserRole
from .models import Resume
from .serializers import ResumeSerializer
from .permissions import IsResumeOwnerOrAdminOrOfficer

class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated, IsResumeOwnerOrAdminOrOfficer]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Resume.objects.none()

        if user.role == UserRole.STUDENT:
            return Resume.objects.filter(student__user=user)
        elif user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            return Resume.objects.all()
        
        # Recruiters and others get no access by default in this view
        return Resume.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != UserRole.STUDENT:
            raise PermissionDenied("Only students can upload resumes.")
        
        try:
            student_profile = user.student_profile
        except hasattr(user, 'student_profile') and getattr(user, 'student_profile'):
            raise ValidationError({"detail": "Student profile not found."})
        except Exception:
            raise ValidationError({"detail": "Student profile not found."})
            
        serializer.save(student=student_profile)

    @action(detail=False, methods=['get'])
    def active(self, request):
        user = request.user
        if user.role != UserRole.STUDENT:
            return Response({"detail": "Only students have active resumes."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            resume = Resume.objects.get(student__user=user, is_active=True)
            serializer = self.get_serializer(resume)
            return Response(serializer.data)
        except Resume.DoesNotExist:
            return Response({"detail": "No active resume found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def versions(self, request):
        user = request.user
        if user.role != UserRole.STUDENT:
            return Response({"detail": "Only students can view resume versions."}, status=status.HTTP_403_FORBIDDEN)
            
        resumes = Resume.objects.filter(student__user=user).order_by('-version_number')
        
        # We need to return specific fields: id, title, version_number, is_active, uploaded_at
        data = []
        for resume in resumes:
            data.append({
                'id': resume.id,
                'title': resume.title,
                'version_number': resume.version_number,
                'is_active': resume.is_active,
                'uploaded_at': resume.uploaded_at
            })
            
        return Response(data)

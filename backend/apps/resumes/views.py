from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.models import UserRole
from .models import Resume, ResumeAnalysis
from .serializers import ResumeSerializer, ResumeAnalysisSerializer
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

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        resume = self.get_object()
        
        if not resume.file:
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            # We open the file here; FileResponse will close it automatically.
            file_handle = resume.file.open('rb')
            response = FileResponse(file_handle, content_type='application/pdf')
            
            import os
            filename = os.path.basename(resume.file.name)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except FileNotFoundError:
            return Response({"detail": "The physical file is missing."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        resume = self.get_object()
        
        # Admin or Placement Officer can view any analysis (as per IsResumeOwnerOrAdminOrOfficer)
        # Student can only view their own, handled by the permission class and get_object()
        
        latest_analysis = resume.analyses.order_by('-analyzed_at').first()
        if not latest_analysis:
            return Response({"detail": "No analysis found for this resume."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = ResumeAnalysisSerializer(latest_analysis)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def analyses(self, request, pk=None):
        resume = self.get_object()
        
        analyses = resume.analyses.order_by('-analyzed_at')
        serializer = ResumeAnalysisSerializer(analyses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        resume = self.get_object()
        
        if not resume.file:
            return Response({"detail": "File not found."}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            from .utils import extract_text_from_pdf, detect_skills
            file_handle = resume.file.open('rb')
            text = extract_text_from_pdf(file_handle)
            file_handle.close()
            
            if text is None:
                return Response({"detail": "Invalid or unreadable PDF file."}, status=status.HTTP_400_BAD_REQUEST)
            
            skills_found = detect_skills(text)
            
            # Create ResumeAnalysis record
            analysis = ResumeAnalysis.objects.create(
                resume=resume,
                score=0.0,
                skills_found=skills_found
            )
            
            return Response({
                "resume_id": resume.id,
                "skills_found": analysis.skills_found,
                "analyzed_at": analysis.analyzed_at
            }, status=status.HTTP_200_OK)
            
        except FileNotFoundError:
            return Response({"detail": "The physical file is missing."}, status=status.HTTP_404_NOT_FOUND)

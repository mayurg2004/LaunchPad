from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CareerRecommendation
from .serializers import CareerRecommendationSerializer
from accounts.models import UserRole
from resumes.models import Resume, ResumeAnalysis
from .career_rules import generate_rule_based_recommendations
from .services import AIService
from rest_framework.views import APIView

class RecommendedDrivesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != UserRole.STUDENT:
            return Response({"error": "Only students can get recommended drives."}, status=status.HTTP_403_FORBIDDEN)
        
        student = getattr(user, 'student_profile', None)
        if not student:
            return Response({"error": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        ai_service = AIService()
        result, status_code = ai_service.get_recommended_drives(student)
        
        return Response(result, status=status_code)

class CareerRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CareerRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role in [UserRole.ADMIN, UserRole.PLACEMENT_OFFICER]:
            return CareerRecommendation.objects.all()
        elif user.role == UserRole.STUDENT:
            return CareerRecommendation.objects.filter(student__user=user)
        return CareerRecommendation.objects.none()

    def _generate_and_save_recommendations(self, request, delete_outdated=False):
        user = request.user
        if user.role != UserRole.STUDENT:
            return Response({"error": "Only students can generate recommendations."}, status=status.HTTP_403_FORBIDDEN)
        
        student = getattr(user, 'student_profile', None)
        if not student:
            return Response({"error": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

        active_resume = Resume.objects.filter(student=student, is_active=True).first()
        if not active_resume:
            return Response({"error": "No active resume found."}, status=status.HTTP_400_BAD_REQUEST)
            
        latest_analysis = ResumeAnalysis.objects.filter(resume=active_resume).order_by('-analyzed_at').first()
        if not latest_analysis:
            return Response({"error": "No resume analysis found. Please analyze your resume first."}, status=status.HTTP_400_BAD_REQUEST)
            
        detected_skills = latest_analysis.skills_found
        recommendations_data = generate_rule_based_recommendations(detected_skills)
        
        new_roles = [rec['role'] for rec in recommendations_data]
        
        if delete_outdated:
            CareerRecommendation.objects.filter(student=student).exclude(recommended_role__in=new_roles).delete()
        
        created_recommendations = []
        for rec_data in recommendations_data:
            rec, created = CareerRecommendation.objects.update_or_create(
                student=student,
                recommended_role=rec_data['role'],
                defaults={
                    'match_score': rec_data['match_score'],
                    'matched_skills': rec_data['matched_skills'],
                    'missing_skills': rec_data['missing_skills'],
                    'explanation': rec_data['explanation']
                }
            )
            created_recommendations.append(rec)
            
        return created_recommendations

    @action(detail=False, methods=['post'])
    def generate(self, request):
        result = self._generate_and_save_recommendations(request, delete_outdated=False)
        if isinstance(result, Response):
            return result
        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        result = self._generate_and_save_recommendations(request, delete_outdated=True)
        if isinstance(result, Response):
            return result
        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

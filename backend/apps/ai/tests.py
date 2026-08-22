from django.test import TestCase
from django.conf import settings
from .services import AIService
from .providers.mock import MockAIProvider

class AIServiceTests(TestCase):
    def test_ai_service_instantiation(self):
        """Test that AIService can be instantiated."""
        service = AIService()
        self.assertIsNotNone(service)
        self.assertIsInstance(service.provider, MockAIProvider)
        
    def test_provider_abstraction(self):
        """Test that the service uses the correct provider based on config."""
        service = AIService(provider_name='mock')
        self.assertIsInstance(service.provider, MockAIProvider)
        
        # Test default fallback when an unknown provider is requested
        service_unknown = AIService(provider_name='unknown')
        self.assertIsInstance(service_unknown.provider, MockAIProvider)

    def test_missing_configuration_handled_cleanly(self):
        """Test that when config is missing or using default, it falls back cleanly."""
        # Force default settings behavior (as if AI_PROVIDER is not set)
        original_provider = getattr(settings, 'AI_PROVIDER', None)
        settings.AI_PROVIDER = 'mock'
        
        service = AIService()
        self.assertIsInstance(service.provider, MockAIProvider)
        
        if original_provider:
            settings.AI_PROVIDER = original_provider

    def test_placeholder_analysis_response_structure(self):
        """Test that placeholder responses have the expected structure."""
        service = AIService()
        
        # Test analyze_resume
        response = service.analyze_resume("sample text")
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["provider"], "mock")
        self.assertIn("message", response)
        
        # Test generate_resume_suggestions
        suggestions_response = service.generate_resume_suggestions("text", ["Python"])
        self.assertIn("suggestions", suggestions_response)
        
        # Test analyze_skill_gap
        gap_response = service.analyze_skill_gap(["Python"], ["Python", "Django"])
        self.assertIn("missing_skills", gap_response)
        self.assertEqual(gap_response["missing_skills"], ["Django"])
        
        # Test generate_career_recommendations
        career_response = service.generate_career_recommendations({"name": "Test"})
        self.assertTrue(len(career_response) > 0)
        self.assertIn("role", career_response[0])

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User, UserRole
from students.models import Student
from .models import CareerRecommendation
from django.core.exceptions import ValidationError

class CareerRecommendationTests(APITestCase):
    def setUp(self):
        # Create student 1
        self.user1 = User.objects.create_user(email='student1@test.com', password='password123', first_name='Student', last_name='One', role=UserRole.STUDENT)
        self.student1 = Student.objects.create(user=self.user1, enrollment_number='EN1', branch='CS', year=3, semester=5, cgpa=8.0)
        
        # Create student 2
        self.user2 = User.objects.create_user(email='student2@test.com', password='password123', first_name='Student', last_name='Two', role=UserRole.STUDENT)
        self.student2 = Student.objects.create(user=self.user2, enrollment_number='EN2', branch='CS', year=3, semester=5, cgpa=7.5)
        
        # Create admin
        self.admin_user = User.objects.create_user(email='admin@test.com', password='password123', first_name='Admin', last_name='User', role=UserRole.ADMIN, is_staff=True)
        
        # Create recommendations
        self.rec1 = CareerRecommendation.objects.create(
            student=self.student1,
            recommended_role='Software Engineer',
            match_score=85.5,
            matched_skills=["Python", "Django"],
            missing_skills=["AWS"],
            explanation="Good match."
        )

        self.list_url = reverse('career-recommendation-list')
        self.detail_url = reverse('career-recommendation-detail', kwargs={'pk': self.rec1.pk})

    def test_recommendation_creation(self):
        """Test that recommendation was created correctly."""
        self.assertEqual(CareerRecommendation.objects.count(), 1)
        self.assertEqual(self.rec1.student, self.student1)
        self.assertEqual(self.rec1.match_score, 85.5)

    def test_student_can_view_own_recommendations(self):
        """Test student can view their own recommendations."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.rec1.id)

        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

    def test_student_cannot_view_another_students_recommendation(self):
        """Test student cannot view another student's recommendations."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) # Should be empty

        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_view_all_recommendations(self):
        """Test admin can view all recommendations."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_invalid_score_is_rejected(self):
        """Test invalid score validation."""
        invalid_rec = CareerRecommendation(
            student=self.student1,
            recommended_role='Invalid',
            match_score=105.0, # Over 100
            explanation="Invalid match."
        )
        with self.assertRaises(ValidationError):
            invalid_rec.full_clean()
            
        invalid_rec2 = CareerRecommendation(
            student=self.student1,
            recommended_role='Invalid',
            match_score=-5.0, # Under 0
            explanation="Invalid match."
        )
        with self.assertRaises(ValidationError):
            invalid_rec2.full_clean()

    def test_empty_recommendation_list_works(self):
        """Test retrieving empty recommendation list."""
        CareerRecommendation.objects.all().delete()
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

from resumes.models import Resume, ResumeAnalysis
from django.core.files.uploadedfile import SimpleUploadedFile

class CareerRecommendationGenerationTests(APITestCase):
    def setUp(self):
        # Create student 1
        self.user1 = User.objects.create_user(email='gen_student1@test.com', password='password123', first_name='Student', last_name='Gen', role=UserRole.STUDENT)
        self.student1 = Student.objects.create(user=self.user1, enrollment_number='GEN1', branch='CS', year=3, semester=5, cgpa=8.0)
        
        self.generate_url = reverse('career-recommendation-generate')

    def _create_resume_with_skills(self, student, skills):
        dummy_file = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")
        resume = Resume.objects.create(student=student, title="Resume", file=dummy_file, is_active=True)
        ResumeAnalysis.objects.create(resume=resume, score=80.0, skills_found=skills)
        return resume

    def test_backend_developer_recommendation(self):
        """Test Backend Developer recommendation."""
        self._create_resume_with_skills(self.student1, ["Python", "Django", "SQL", "Git"])
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.generate_url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should match Backend Developer 100%, and Machine Learning Engineer 50%
        # Let's find backend dev in response
        backend_rec = next((r for r in response.data if r['recommended_role'] == 'Backend Developer'), None)
        self.assertIsNotNone(backend_rec)
        self.assertEqual(backend_rec['match_score'], 100.0)
        self.assertEqual(len(backend_rec['missing_skills']), 0)

    def test_frontend_developer_recommendation(self):
        """Test Frontend Developer recommendation."""
        self._create_resume_with_skills(self.student1, ["JavaScript", "React", "HTML", "CSS"])
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.generate_url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        frontend_rec = next((r for r in response.data if r['recommended_role'] == 'Frontend Developer'), None)
        self.assertIsNotNone(frontend_rec)
        self.assertEqual(frontend_rec['match_score'], 100.0)

    def test_flutter_developer_recommendation(self):
        """Test Flutter Developer recommendation."""
        self._create_resume_with_skills(self.student1, ["Flutter", "Dart"])
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.generate_url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        flutter_rec = next((r for r in response.data if r['recommended_role'] == 'Flutter Developer'), None)
        self.assertIsNotNone(flutter_rec)
        self.assertEqual(flutter_rec['match_score'], 100.0)

    def test_devops_recommendation(self):
        """Test DevOps Engineer recommendation."""
        self._create_resume_with_skills(self.student1, ["Docker", "AWS", "Linux"])
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.generate_url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        devops_rec = next((r for r in response.data if r['recommended_role'] == 'DevOps Engineer'), None)
        self.assertIsNotNone(devops_rec)
        self.assertEqual(devops_rec['match_score'], 100.0)

    def test_machine_learning_recommendation(self):
        """Test Machine Learning Engineer recommendation."""
        self._create_resume_with_skills(self.student1, ["Python", "Machine Learning"])
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.generate_url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ml_rec = next((r for r in response.data if r['recommended_role'] == 'Machine Learning Engineer'), None)
        self.assertIsNotNone(ml_rec)
        self.assertEqual(ml_rec['match_score'], 100.0)

    def test_missing_skills_and_match_score(self):
        """Test missing skills and match score calculation."""
        # Backend needs Python, Django, SQL (3 skills)
        # Providing only Python (1 skill) -> score should be 33.33%
        self._create_resume_with_skills(self.student1, ["Python", "Git"])
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.generate_url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        backend_rec = next((r for r in response.data if r['recommended_role'] == 'Backend Developer'), None)
        self.assertIsNotNone(backend_rec)
        self.assertAlmostEqual(backend_rec['match_score'], 33.33, places=2)
        self.assertIn("Django", backend_rec['missing_skills'])
        self.assertIn("SQL", backend_rec['missing_skills'])

    def test_student_without_resume(self):
        """Test generating recommendation when student has no active resume."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.generate_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "No active resume found.")

    def test_student_without_resume_analysis(self):
        """Test generating recommendation when student has resume but no analysis."""
        dummy_file = SimpleUploadedFile("resume.pdf", b"file_content", content_type="application/pdf")
        Resume.objects.create(student=self.student1, title="Resume", file=dummy_file, is_active=True)
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.generate_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "No resume analysis found. Please analyze your resume first.")

    def test_unauthorized_access(self):
        """Test that non-students (e.g. recruiters) cannot generate recommendations."""
        admin_user = User.objects.create_user(email='admin_gen@test.com', password='password', role=UserRole.ADMIN)
        self.client.force_authenticate(user=admin_user)
        
        response = self.client.post(self.generate_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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

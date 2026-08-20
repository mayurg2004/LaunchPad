import io
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, UserRole
from students.models import Student
from resumes.models import Resume, ResumeAnalysis
from ai.services import AIService

class ResumeAIAnalyzeTests(APITestCase):
    def setUp(self):
        # Create student user
        self.student_user = User.objects.create_user(
            email='student1@example.com',
            password='password123',
            role=UserRole.STUDENT,
            first_name='Student',
            last_name='One'
        )
        self.student = Student.objects.create(
            user=self.student_user, 
            phone_number='1234567890', 
            year=3,
            semester=5,
            enrollment_number='STU1',
            branch='CSE',
            cgpa=8.0
        )
        
        # Create another student user
        self.student_user2 = User.objects.create_user(
            email='student2@example.com',
            password='password123',
            role=UserRole.STUDENT,
            first_name='Student',
            last_name='Two'
        )
        self.student2 = Student.objects.create(
            user=self.student_user2, 
            phone_number='0987654321', 
            year=3,
            semester=5,
            enrollment_number='STU2',
            branch='CSE',
            cgpa=8.5
        )
        
    def generate_pdf(self, content=b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"):
        return SimpleUploadedFile("test_resume.pdf", content, content_type="application/pdf")

    @patch('resumes.utils.extract_text_from_pdf')
    @patch('ai.services.AIService.analyze_resume')
    def test_authenticated_student_can_request_ai_analysis(self, mock_analyze, mock_extract):
        mock_extract.return_value = "Sample extracted text"
        mock_analyze.return_value = {
            "score": 85,
            "strengths": ["Good formatting"],
            "weaknesses": ["Needs more detail"],
            "skills_found": ["Python", "Django"],
            "suggestions": ["Add metrics"]
        }
        
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        url = reverse('resume-ai-analyze', kwargs={'pk': resume.id})
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 85)
        self.assertIn('weaknesses', response.data)
        
        # Verify saved in DB
        analysis = ResumeAnalysis.objects.filter(resume=resume).first()
        self.assertIsNotNone(analysis)
        self.assertEqual(analysis.score, 85)
        self.assertEqual(analysis.weaknesses, ["Needs more detail"])
        
        mock_extract.assert_called_once()
        mock_analyze.assert_called_once_with("Sample extracted text")

    def test_student_cannot_analyze_another_students_resume(self):
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        url = reverse('resume-ai-analyze', kwargs={'pk': resume.id})
        
        self.client.force_authenticate(user=self.student_user2)
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('resumes.utils.extract_text_from_pdf')
    @patch('ai.services.AIService.analyze_resume')
    def test_missing_ai_configuration_handled(self, mock_analyze, mock_extract):
        mock_extract.return_value = "Sample text"
        mock_analyze.side_effect = ValueError("AI_API_KEY is missing or not configured.")
        
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        url = reverse('resume-ai-analyze', kwargs={'pk': resume.id})
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("AI_API_KEY is missing", response.data['detail'])

    @patch('resumes.utils.extract_text_from_pdf')
    @patch('ai.services.AIService.analyze_resume')
    def test_invalid_provider_response_handled(self, mock_analyze, mock_extract):
        mock_extract.return_value = "Sample text"
        mock_analyze.side_effect = Exception("Some unknown error")
        
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        url = reverse('resume-ai-analyze', kwargs={'pk': resume.id})
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['detail'], "AI Provider Error.")

    @patch('resumes.utils.extract_text_from_pdf')
    @patch('ai.services.AIService.analyze_resume')
    def test_score_validation_works(self, mock_analyze, mock_extract):
        mock_extract.return_value = "Sample text"
        # AI returns invalid score
        mock_analyze.return_value = {
            "score": 150,  # Invalid
            "strengths": [],
            "weaknesses": [],
            "skills_found": [],
            "suggestions": []
        }
        
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        url = reverse('resume-ai-analyze', kwargs={'pk': resume.id})
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("score must be between 0 and 100", response.data['detail'])

    @patch('resumes.utils.extract_text_from_pdf')
    def test_empty_resume_handled(self, mock_extract):
        mock_extract.return_value = "   " # empty after strip
        
        resume = Resume.objects.create(student=self.student, title='R1', file=self.generate_pdf())
        url = reverse('resume-ai-analyze', kwargs={'pk': resume.id})
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid or unreadable PDF file", response.data['detail'])

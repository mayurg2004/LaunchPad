from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User, UserRole
from students.models import Student
from placement_drive.models import PlacementDrive
from companies.models import Company
from applications.models import Application
from interviews.models import Interview

class InterviewAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.student_user = User.objects.create_user(email='student1@test.com', password='testpassword', role=UserRole.STUDENT)
        self.officer_user = User.objects.create_user(email='officer@test.com', password='testpassword', role=UserRole.PLACEMENT_OFFICER)
        
        # Create students
        self.student = Student.objects.create(
            user=self.student_user,
            enrollment_number="ENR001",
            branch="CSE",
            year=4,
            semester=8,
            cgpa=8.5
        )
        
        # Create company
        self.company = Company.objects.create(company_name="Tech Corp")
        
        # Create drive
        self.open_drive = PlacementDrive.objects.create(
            company=self.company,
            title="SDE Hiring",
            job_role="SDE",
            status="OPEN",
            application_deadline=timezone.now() + timedelta(days=2),
            minimum_cgpa=7.0,
            eligible_branch="CSE, ISE"
        )
        
        # Create application
        self.application = Application.objects.create(
            student=self.student,
            placement_drive=self.open_drive,
            status="SHORTLISTED"
        )
        
        self.url = '/api/interviews/'
        self.future_date = timezone.now() + timedelta(days=1)

    def test_create_interview(self):
        self.client.force_authenticate(user=self.officer_user)
        data = {
            'application': self.application.id,
            'round_name': 'Technical Round 1',
            'round_type': 'TECHNICAL',
            'scheduled_at': self.future_date.isoformat(),
            'duration_minutes': 60
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Interview.objects.count(), 1)
        
    def test_create_interview_invalid_data(self):
        # Test past scheduled_at
        self.client.force_authenticate(user=self.officer_user)
        past_date = timezone.now() - timedelta(days=1)
        data = {
            'application': self.application.id,
            'round_name': 'Technical Round 1',
            'round_type': 'TECHNICAL',
            'scheduled_at': past_date.isoformat(),
            'duration_minutes': 60
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('scheduled_at', response.data)

    def test_retrieve_interview(self):
        interview = Interview.objects.create(
            application=self.application,
            round_name='HR Round',
            round_type='HR',
            scheduled_at=self.future_date
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f'{self.url}{interview.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['round_name'], 'HR Round')

    def test_update_interview(self):
        interview = Interview.objects.create(
            application=self.application,
            round_name='HR Round',
            round_type='HR',
            scheduled_at=self.future_date
        )
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.patch(f'{self.url}{interview.id}/', {'status': 'COMPLETED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        interview.refresh_from_db()
        self.assertEqual(interview.status, 'COMPLETED')
        
    def test_delete_interview(self):
        interview = Interview.objects.create(
            application=self.application,
            round_name='HR Round',
            round_type='HR',
            scheduled_at=self.future_date
        )
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.delete(f'{self.url}{interview.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Interview.objects.count(), 0)
        
    def test_student_cannot_create_or_update(self):
        interview = Interview.objects.create(
            application=self.application,
            round_name='HR Round',
            round_type='HR',
            scheduled_at=self.future_date
        )
        self.client.force_authenticate(user=self.student_user)
        
        # POST
        data = {
            'application': self.application.id,
            'round_name': 'Technical Round 1',
            'round_type': 'TECHNICAL',
            'scheduled_at': self.future_date.isoformat(),
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # PATCH
        response = self.client.patch(f'{self.url}{interview.id}/', {'status': 'COMPLETED'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

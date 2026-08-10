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

    def test_admin_permissions(self):
        admin_user = User.objects.create_user(email='admin@test.com', password='testpassword', role=UserRole.ADMIN)
        interview = Interview.objects.create(
            application=self.application,
            round_name='Admin Round',
            round_type='TECHNICAL',
            scheduled_at=self.future_date
        )
        self.client.force_authenticate(user=admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin can update
        response = self.client.patch(f'{self.url}{interview.id}/', {'status': 'CANCELLED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_status_update_endpoint(self):
        interview = Interview.objects.create(
            application=self.application,
            round_name='HR Round',
            round_type='HR',
            scheduled_at=self.future_date
        )
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.patch(f'{self.url}{interview.id}/status/', {'status': 'COMPLETED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        interview.refresh_from_db()
        self.assertEqual(interview.status, 'COMPLETED')
        
        # Invalid status
        response = self.client.patch(f'{self.url}{interview.id}/status/', {'status': 'INVALID'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)

    def test_result_update_endpoint(self):
        interview = Interview.objects.create(
            application=self.application,
            round_name='HR Round',
            round_type='HR',
            scheduled_at=self.future_date
        )
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.patch(f'{self.url}{interview.id}/result/', {'result': 'PASSED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        interview.refresh_from_db()
        self.assertEqual(interview.result, 'PASSED')
        
        # Invalid result
        response = self.client.patch(f'{self.url}{interview.id}/result/', {'result': 'INVALID'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('result', response.data)
        
    def test_recruiter_permissions(self):
        # We simulate a recruiter by creating a user and attaching a mock profile
        recruiter_user = User.objects.create_user(email='recruiter@test.com', password='testpassword', role=UserRole.RECRUITER)
        
        class MockRecruiterProfile:
            pass
            
        mock_profile = MockRecruiterProfile()
        mock_profile.company = self.company
        recruiter_user.recruiter_profile = mock_profile
        
        interview = Interview.objects.create(
            application=self.application,
            round_name='Tech Round',
            round_type='TECHNICAL',
            scheduled_at=self.future_date
        )
        
        self.client.force_authenticate(user=recruiter_user)
        
        # Should be able to view and manage for their company
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Try status update
        response = self.client.patch(f'{self.url}{interview.id}/status/', {'status': 'IN_PROGRESS'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_interview_filtering(self):
        Interview.objects.create(
            application=self.application,
            round_name='Tech Round',
            round_type='TECHNICAL',
            scheduled_at=self.future_date,
            status='SCHEDULED',
            result='PENDING'
        )
        Interview.objects.create(
            application=self.application,
            round_name='HR Round',
            round_type='HR',
            scheduled_at=self.future_date,
            status='COMPLETED',
            result='PASSED'
        )
        
        self.client.force_authenticate(user=self.officer_user)
        
        # Filter by round_type
        response = self.client.get(f'{self.url}?round_type=HR')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['round_type'], 'HR')
        
        # Filter by status
        response = self.client.get(f'{self.url}?status=COMPLETED')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'COMPLETED')
        
        # Filter by result
        response = self.client.get(f'{self.url}?result=PASSED')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['result'], 'PASSED')

    def test_interview_ordering(self):
        interview1 = Interview.objects.create(
            application=self.application,
            round_name='Round 1',
            round_type='TECHNICAL',
            scheduled_at=self.future_date + timedelta(days=2)
        )
        interview2 = Interview.objects.create(
            application=self.application,
            round_name='Round 2',
            round_type='HR',
            scheduled_at=self.future_date + timedelta(days=1)
        )
        
        self.client.force_authenticate(user=self.officer_user)
        
        # Order by scheduled_at (ascending)
        response = self.client.get(f'{self.url}?ordering=scheduled_at')
        self.assertEqual(response.data[0]['id'], interview2.id)
        self.assertEqual(response.data[1]['id'], interview1.id)
        
        # Order by scheduled_at (descending)
        response = self.client.get(f'{self.url}?ordering=-scheduled_at')
        self.assertEqual(response.data[0]['id'], interview1.id)
        self.assertEqual(response.data[1]['id'], interview2.id)

    def test_upcoming_interviews(self):
        # 1. Valid upcoming
        valid_upcoming = Interview.objects.create(
            application=self.application,
            round_name='Upcoming Round',
            round_type='TECHNICAL',
            scheduled_at=self.future_date + timedelta(days=1),
            status='SCHEDULED'
        )
        
        # 2. Nearest upcoming
        nearest_upcoming = Interview.objects.create(
            application=self.application,
            round_name='Nearest Upcoming',
            round_type='TECHNICAL',
            scheduled_at=self.future_date,
            status='SCHEDULED'
        )
        
        # 3. Past interview (should be excluded)
        # Bypassing validation by updating DB directly or just mocking time
        past_interview = Interview(
            application=self.application,
            round_name='Past Round',
            round_type='TECHNICAL',
            scheduled_at=timezone.now() - timedelta(days=1),
            status='SCHEDULED'
        )
        past_interview.save()
        
        # 4. Cancelled interview (should be excluded)
        cancelled_interview = Interview.objects.create(
            application=self.application,
            round_name='Cancelled Round',
            round_type='TECHNICAL',
            scheduled_at=self.future_date + timedelta(days=2),
            status='CANCELLED'
        )
        
        # 5. Other student's upcoming interview (should be excluded)
        other_student_user = User.objects.create_user(email='other@test.com', password='testpassword', role=UserRole.STUDENT)
        other_student = Student.objects.create(
            user=other_student_user,
            enrollment_number="ENR002",
            branch="CSE",
            year=4,
            semester=8,
            cgpa=8.5
        )
        other_app = Application.objects.create(
            student=other_student,
            placement_drive=self.open_drive,
            status="SHORTLISTED"
        )
        other_upcoming = Interview.objects.create(
            application=other_app,
            round_name='Other Student Upcoming',
            round_type='TECHNICAL',
            scheduled_at=self.future_date,
            status='SCHEDULED'
        )
        
        self.client.force_authenticate(user=self.student_user)
        
        response = self.client.get(f'{self.url}upcoming/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only contain nearest_upcoming and valid_upcoming, in that order
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['id'], nearest_upcoming.id)
        self.assertEqual(response.data[1]['id'], valid_upcoming.id)


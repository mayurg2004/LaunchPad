from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from django.db import IntegrityError

from accounts.models import User, UserRole
from students.models import Student
from placement_drive.models import PlacementDrive
from companies.models import Company
from applications.models import Application

class ApplicationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.student_user = User.objects.create_user(email='student1@test.com', password='testpassword', role=UserRole.STUDENT)
        self.student2_user = User.objects.create_user(email='student2@test.com', password='testpassword', role=UserRole.STUDENT)
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
        self.student2 = Student.objects.create(
            user=self.student2_user,
            enrollment_number="ENR002",
            branch="MECH",
            year=4,
            semester=8,
            cgpa=6.0
        )
        
        # Create company
        self.company = Company.objects.create(company_name="Tech Corp")
        
        # Create drives
        self.open_drive = PlacementDrive.objects.create(
            company=self.company,
            title="SDE Hiring",
            job_role="SDE",
            status="OPEN",
            application_deadline=timezone.now() + timedelta(days=2),
            minimum_cgpa=7.0,
            eligible_branch="CSE, ISE"
        )
        
        self.closed_drive = PlacementDrive.objects.create(
            company=self.company,
            title="Old Hiring",
            job_role="SDE",
            status="CLOSED",
        )

        self.url = '/api/applications/'

    def test_student_can_apply_open_drive(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.url, {'placement_drive': self.open_drive.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Application.objects.count(), 1)
        
    def test_student_cannot_apply_twice(self):
        self.client.force_authenticate(user=self.student_user)
        self.client.post(self.url, {'placement_drive': self.open_drive.id})
        
        # Second application
        response = self.client.post(self.url, {'placement_drive': self.open_drive.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Application.objects.count(), 1)
        
    def test_student_cannot_apply_closed_drive(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.url, {'placement_drive': self.closed_drive.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_student_cannot_apply_past_deadline(self):
        past_drive = PlacementDrive.objects.create(
            company=self.company,
            title="Past Deadline Hiring",
            job_role="SDE",
            status="OPEN",
            application_deadline=timezone.now() - timedelta(days=1)
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.post(self.url, {'placement_drive': past_drive.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_ineligible_student_cannot_apply(self):
        # Student 2 is MECH and 6.0 CGPA (Drive requires CSE, ISE and 7.0 CGPA)
        self.client.force_authenticate(user=self.student2_user)
        response = self.client.post(self.url, {'placement_drive': self.open_drive.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_can_view_own_applications(self):
        Application.objects.create(student=self.student, placement_drive=self.open_drive)
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming pagination is in place by default generic viewsets depending on settings,
        # but if no global pagination, it will be a list. Let's check results or root.
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)
        
    def test_student_cannot_view_others_applications(self):
        Application.objects.create(student=self.student, placement_drive=self.open_drive)
        
        # Authenticate as student2
        self.client.force_authenticate(user=self.student2_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 0)
        else:
            self.assertEqual(len(response.data), 0)
        
    def test_placement_officer_can_view_all(self):
        Application.objects.create(student=self.student, placement_drive=self.open_drive)
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_officer_can_update_status(self):
        app = Application.objects.create(student=self.student, placement_drive=self.open_drive)
        self.client.force_authenticate(user=self.officer_user)
        
        url = f"{self.url}{app.id}/status/"
        response = self.client.patch(url, {'status': 'SHORTLISTED'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, 'SHORTLISTED')

    def test_unauthorized_user_cannot_update_status(self):
        app = Application.objects.create(student=self.student, placement_drive=self.open_drive)
        self.client.force_authenticate(user=self.student_user) # Student tries to update
        
        url = f"{self.url}{app.id}/status/"
        response = self.client.patch(url, {'status': 'SHORTLISTED'})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_db_unique_constraint(self):
        Application.objects.create(student=self.student, placement_drive=self.open_drive)
        with self.assertRaises(IntegrityError):
            Application.objects.create(student=self.student, placement_drive=self.open_drive)

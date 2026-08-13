from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone

from accounts.models import User, UserRole
from students.models import Student
from companies.models import Company
from placement_drive.models import PlacementDrive
from applications.models import Application
from interviews.models import Interview
from offers.models import Offer

class AnalyticsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('analytics-overview')

        # Create users with different roles
        self.admin_user = User.objects.create_user(email='admin@test.com', password='password', role=UserRole.ADMIN, first_name='A', last_name='A')
        self.po_user = User.objects.create_user(email='po@test.com', password='password', role=UserRole.PLACEMENT_OFFICER, first_name='P', last_name='O')
        self.student_user = User.objects.create_user(email='student@test.com', password='password', role=UserRole.STUDENT, first_name='S', last_name='S')
        self.recruiter_user = User.objects.create_user(email='recruiter@test.com', password='password', role=UserRole.RECRUITER, first_name='R', last_name='R')

    def test_permissions(self):
        # 1. Admin can access analytics.
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Placement Officer can access analytics.
        self.client.force_authenticate(user=self.po_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Student cannot access analytics.
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 4. Recruiter cannot access analytics.
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Unauthenticated
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_analytics_calculations(self):
        # Create some data
        s1 = Student.objects.create(user=self.student_user, enrollment_number='S1', branch='CSE', year=4, semester=8, cgpa=8.5, is_placed=True)
        
        student_user2 = User.objects.create_user(email='student2@test.com', password='password', role=UserRole.STUDENT, first_name='S2', last_name='S2')
        s2 = Student.objects.create(user=student_user2, enrollment_number='S2', branch='ECE', year=4, semester=8, cgpa=7.5, is_placed=False)
        
        c1 = Company.objects.create(company_name='Company A')
        c2 = Company.objects.create(company_name='Company B')
        
        pd1 = PlacementDrive.objects.create(company=c1, title='Drive 1', job_role='SDE')
        
        a1 = Application.objects.create(student=s1, placement_drive=pd1)
        a2 = Application.objects.create(student=s2, placement_drive=pd1)
        
        i1 = Interview.objects.create(application=a1, round_name='Round 1', round_type='TECHNICAL', scheduled_at=timezone.now())
        i2 = Interview.objects.create(application=a1, round_name='Round 2', round_type='HR', scheduled_at=timezone.now())
        
        o1 = Offer.objects.create(application=a1, student=s1, company=c1, placement_drive=pd1, offer_type='FULL_TIME', job_title='SDE', package_lpa=10, joining_location='Bangalore', joining_date=timezone.now().date(), offer_date=timezone.now().date())

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # 5. Total students count is correct.
        self.assertEqual(data['total_students'], 2)
        
        # 6. Total companies count is correct.
        self.assertEqual(data['total_companies'], 2)
        
        # 7. Total placement drives count is correct.
        self.assertEqual(data['total_placement_drives'], 1)
        
        # 8. Total applications count is correct.
        self.assertEqual(data['total_applications'], 2)
        
        # 9. Total interviews count is correct.
        self.assertEqual(data['total_interviews'], 2)
        
        # 10. Total offers count is correct.
        self.assertEqual(data['total_offers'], 1)
        
        # 11. Placed students count is correct.
        self.assertEqual(data['placed_students'], 1)
        
        # 12. Placement percentage is calculated correctly.
        self.assertEqual(data['placement_percentage'], 50.0)

    def test_zero_students_division(self):
        # 13. Zero students does not cause a division-by-zero error.
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(data['total_students'], 0)
        self.assertEqual(data['placement_percentage'], 0.0)

class DepartmentAnalyticsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('analytics-departments')

        # Create users with different roles
        self.admin_user = User.objects.create_user(email='admin@test.com', password='password', role=UserRole.ADMIN, first_name='A', last_name='A')
        self.po_user = User.objects.create_user(email='po@test.com', password='password', role=UserRole.PLACEMENT_OFFICER, first_name='P', last_name='O')
        self.student_user = User.objects.create_user(email='student@test.com', password='password', role=UserRole.STUDENT, first_name='S', last_name='S')
        self.recruiter_user = User.objects.create_user(email='recruiter@test.com', password='password', role=UserRole.RECRUITER, first_name='R', last_name='R')

    def test_permissions(self):
        # 1. Admin can access department analytics.
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. Placement Officer can access department analytics.
        self.client.force_authenticate(user=self.po_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Student cannot access department analytics.
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # 4. Recruiter cannot access department analytics.
        self.client.force_authenticate(user=self.recruiter_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_department_calculations_and_ordering(self):
        # Create data for branches
        # CSE: 2 students, 2 placed (100%)
        # IT: 3 students, 2 placed (66.67%)
        # ECE: 1 student, 0 placed (0%)
        
        # CSE
        u1 = User.objects.create_user(email='s1@test.com', password='password', role=UserRole.STUDENT, first_name='A', last_name='B')
        Student.objects.create(user=u1, enrollment_number='S1', branch='CSE', year=4, semester=8, cgpa=8.5, is_placed=True)
        u2 = User.objects.create_user(email='s2@test.com', password='password', role=UserRole.STUDENT, first_name='C', last_name='D')
        Student.objects.create(user=u2, enrollment_number='S2', branch='CSE', year=4, semester=8, cgpa=8.5, is_placed=True)

        # IT
        u3 = User.objects.create_user(email='s3@test.com', password='password', role=UserRole.STUDENT, first_name='E', last_name='F')
        Student.objects.create(user=u3, enrollment_number='S3', branch='IT', year=4, semester=8, cgpa=8.5, is_placed=True)
        u4 = User.objects.create_user(email='s4@test.com', password='password', role=UserRole.STUDENT, first_name='G', last_name='H')
        Student.objects.create(user=u4, enrollment_number='S4', branch='IT', year=4, semester=8, cgpa=8.5, is_placed=True)
        u5 = User.objects.create_user(email='s5@test.com', password='password', role=UserRole.STUDENT, first_name='I', last_name='J')
        Student.objects.create(user=u5, enrollment_number='S5', branch='IT', year=4, semester=8, cgpa=8.5, is_placed=False)

        # ECE
        u6 = User.objects.create_user(email='s6@test.com', password='password', role=UserRole.STUDENT, first_name='K', last_name='L')
        Student.objects.create(user=u6, enrollment_number='S6', branch='ECE', year=4, semester=8, cgpa=8.5, is_placed=False)

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # 8. Multiple branches are returned.
        self.assertEqual(len(data), 3)

        # 10. Results are ordered by placement percentage descending.
        self.assertEqual(data[0]['branch'], 'CSE')
        self.assertEqual(data[1]['branch'], 'IT')
        self.assertEqual(data[2]['branch'], 'ECE')

        # 5. Students are grouped correctly by branch.
        # 6. Placed students are counted correctly.
        # 7. Placement percentage is calculated correctly.
        
        # CSE Checks
        self.assertEqual(data[0]['total_students'], 2)
        self.assertEqual(data[0]['placed_students'], 2)
        self.assertEqual(data[0]['placement_percentage'], 100.0)

        # IT Checks
        self.assertEqual(data[1]['total_students'], 3)
        self.assertEqual(data[1]['placed_students'], 2)
        self.assertEqual(data[1]['placement_percentage'], 66.67)

        # ECE Checks
        self.assertEqual(data[2]['total_students'], 1)
        self.assertEqual(data[2]['placed_students'], 0)
        self.assertEqual(data[2]['placement_percentage'], 0.0)

    def test_zero_students(self):
        # 9. Zero-student/empty data is handled safely.
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(len(data), 0)

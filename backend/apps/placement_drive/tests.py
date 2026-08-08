from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from placement_drive.models import PlacementDrive
from companies.models import Company
from accounts.models import User

class PlacementDriveAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='testpassword', role='ADMIN')
        self.client.force_authenticate(user=self.user)
        
        self.company = Company.objects.create(
            company_name="Test Company",
            company_type="SERVICE",
            email="hr@test.com"
        )
        
        self.drive = PlacementDrive.objects.create(
            company=self.company,
            title="Software Engineer Hiring",
            job_role="Software Engineer",
            package_lpa=10.5,
            minimum_cgpa=7.0
        )
        self.url = '/api/placement-drives/'

    def test_get_drives(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_drive(self):
        data = {
            'company': self.company.id,
            'title': 'Frontend Developer Hiring',
            'job_role': 'Frontend Developer',
            'package_lpa': 12.0,
            'status': 'UPCOMING'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlacementDrive.objects.count(), 2)

    def test_get_single_drive(self):
        url = f"{self.url}{self.drive.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Software Engineer Hiring")

    def test_update_drive(self):
        url = f"{self.url}{self.drive.id}/"
        data = {'title': 'Updated Hiring', 'company': self.company.id, 'job_role': 'Software Engineer'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PlacementDrive.objects.get(id=self.drive.id).title, 'Updated Hiring')

    def test_delete_drive(self):
        url = f"{self.url}{self.drive.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PlacementDrive.objects.count(), 0)

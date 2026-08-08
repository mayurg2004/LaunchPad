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

    def test_search_drives(self):
        # Create a second drive to verify search
        PlacementDrive.objects.create(
            company=self.company,
            title="Data Scientist Hiring",
            job_role="Data Scientist",
            package_lpa=15.0,
            status="UPCOMING"
        )
        
        # Search by title
        response = self.client.get(f"{self.url}?search=Software")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Software Engineer Hiring")
        
        # Search by job role
        response = self.client.get(f"{self.url}?search=Scientist")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Data Scientist Hiring")
        
        # Search by company name
        response = self.client.get(f"{self.url}?search=Test Company")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_drives(self):
        new_company = Company.objects.create(
            company_name="Another Company",
            company_type="PRODUCT",
            email="hr2@test.com"
        )
        PlacementDrive.objects.create(
            company=new_company,
            title="Backend Developer Hiring",
            job_role="Backend Developer",
            package_lpa=14.0,
            minimum_cgpa=8.5,
            status="OPEN"
        )
        
        # Filter by company
        response = self.client.get(f"{self.url}?company={new_company.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['company'], new_company.id)

        # Filter by status
        response = self.client.get(f"{self.url}?status=OPEN")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], "OPEN")

        # Filter by minimum_cgpa
        response = self.client.get(f"{self.url}?minimum_cgpa=8.5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['minimum_cgpa'], "8.50")

    def test_ordering_drives(self):
        PlacementDrive.objects.create(
            company=self.company,
            title="Drive 1",
            job_role="Role 1",
            package_lpa=8.0,
            status="UPCOMING"
        )
        PlacementDrive.objects.create(
            company=self.company,
            title="Drive 2",
            job_role="Role 2",
            package_lpa=12.0,
            status="OPEN"
        )
        PlacementDrive.objects.create(
            company=self.company,
            title="Drive 3",
            job_role="Role 3",
            package_lpa=6.0,
            status="COMPLETED"
        )
        
        # Order by package_lpa (ascending)
        response = self.client.get(f"{self.url}?ordering=package_lpa")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        packages = [float(drive['package_lpa']) for drive in response.data if drive['package_lpa'] is not None]
        self.assertEqual(packages, sorted(packages))

        # Order by package_lpa (descending)
        response = self.client.get(f"{self.url}?ordering=-package_lpa")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        packages_desc = [float(drive['package_lpa']) for drive in response.data if drive['package_lpa'] is not None]
        self.assertEqual(packages_desc, sorted(packages_desc, reverse=True))

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, date
from rest_framework import status
from rest_framework.test import APIClient
from django.db import IntegrityError

from accounts.models import User, UserRole
from students.models import Student
from placement_drive.models import PlacementDrive
from companies.models import Company
from applications.models import Application
from offers.models import Offer

class OfferAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.student_user = User.objects.create_user(email='student1@test.com', password='testpassword', role=UserRole.STUDENT)
        self.officer_user = User.objects.create_user(email='officer@test.com', password='testpassword', role=UserRole.PLACEMENT_OFFICER)
        
        # Create student
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
        self.drive = PlacementDrive.objects.create(
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
            placement_drive=self.drive,
            status="SELECTED"
        )

        self.url = '/api/offers/'
        
        self.valid_payload = {
            'application': self.application.id,
            'student': self.student.id,
            'company': self.company.id,
            'placement_drive': self.drive.id,
            'offer_type': 'FULL_TIME',
            'job_title': 'SDE',
            'package_lpa': '10.50',
            'joining_location': 'Bangalore',
            'joining_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'offer_date': date.today().strftime('%Y-%m-%d'),
            'status': 'PENDING'
        }

    def test_create_offer(self):
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)

    def test_retrieve_offer(self):
        offer = Offer.objects.create(
            application=self.application,
            student=self.student,
            company=self.company,
            placement_drive=self.drive,
            offer_type='FULL_TIME',
            job_title='SDE',
            package_lpa='10.50',
            joining_location='Bangalore',
            joining_date=date.today() + timedelta(days=30),
            offer_date=date.today(),
            status='PENDING'
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f"{self.url}{offer.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['job_title'], 'SDE')

    def test_update_offer(self):
        offer = Offer.objects.create(
            application=self.application,
            student=self.student,
            company=self.company,
            placement_drive=self.drive,
            offer_type='FULL_TIME',
            job_title='SDE',
            package_lpa='10.50',
            joining_location='Bangalore',
            joining_date=date.today() + timedelta(days=30),
            offer_date=date.today(),
            status='PENDING'
        )
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.patch(f"{self.url}{offer.id}/", {'status': 'ACCEPTED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offer.refresh_from_db()
        self.assertEqual(offer.status, 'ACCEPTED')

    def test_validation_package_lpa(self):
        self.client.force_authenticate(user=self.officer_user)
        payload = self.valid_payload.copy()
        payload['package_lpa'] = '0.00'
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('package_lpa', response.data)

    def test_validation_joining_date_before_offer_date(self):
        self.client.force_authenticate(user=self.officer_user)
        payload = self.valid_payload.copy()
        payload['joining_date'] = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('joining_date', response.data)

    def test_duplicate_active_offer_prevention_serializer(self):
        self.client.force_authenticate(user=self.officer_user)
        # Create first offer
        self.client.post(self.url, self.valid_payload)
        
        # Try to create second active offer
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Offer.objects.count(), 1)
        
    def test_allow_multiple_offers_if_rejected(self):
        self.client.force_authenticate(user=self.officer_user)
        # Create first offer and set to REJECTED
        payload1 = self.valid_payload.copy()
        payload1['status'] = 'REJECTED'
        self.client.post(self.url, payload1)
        
        # Try to create second active offer
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 2)

    def test_db_unique_constraint(self):
        Offer.objects.create(
            application=self.application,
            student=self.student,
            company=self.company,
            placement_drive=self.drive,
            offer_type='FULL_TIME',
            job_title='SDE',
            package_lpa='10.50',
            joining_location='Bangalore',
            joining_date=date.today() + timedelta(days=30),
            offer_date=date.today(),
            status='PENDING'
        )
        with self.assertRaises(IntegrityError):
            Offer.objects.create(
                application=self.application,
                student=self.student,
                company=self.company,
                placement_drive=self.drive,
                offer_type='FULL_TIME',
                job_title='SDE2',
                package_lpa='12.50',
                joining_location='Bangalore',
                joining_date=date.today() + timedelta(days=30),
                offer_date=date.today(),
                status='PENDING'
            )

    def test_student_accepts_own_offer(self):
        offer = Offer.objects.create(
            application=self.application,
            student=self.student,
            company=self.company,
            placement_drive=self.drive,
            offer_type='FULL_TIME',
            job_title='SDE',
            package_lpa='10.50',
            joining_location='Bangalore',
            joining_date=date.today() + timedelta(days=30),
            offer_date=date.today(),
            status='PENDING'
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.patch(f"{self.url}{offer.id}/respond/", {'status': 'ACCEPTED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        offer.refresh_from_db()
        self.assertEqual(offer.status, 'ACCEPTED')
        
        # Check student is placed
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_placed)
        
        # Check application status
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'SELECTED')

    def test_student_rejects_own_offer(self):
        offer = Offer.objects.create(
            application=self.application,
            student=self.student,
            company=self.company,
            placement_drive=self.drive,
            offer_type='FULL_TIME',
            job_title='SDE',
            package_lpa='10.50',
            joining_location='Bangalore',
            joining_date=date.today() + timedelta(days=30),
            offer_date=date.today(),
            status='PENDING'
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.patch(f"{self.url}{offer.id}/respond/", {'status': 'REJECTED'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        offer.refresh_from_db()
        self.assertEqual(offer.status, 'REJECTED')
        
        # Check student is not placed
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_placed)

    def test_student_cannot_respond_to_others_offer(self):
        offer = Offer.objects.create(
            application=self.application,
            student=self.student,
            company=self.company,
            placement_drive=self.drive,
            offer_type='FULL_TIME',
            job_title='SDE',
            package_lpa='10.50',
            joining_location='Bangalore',
            joining_date=date.today() + timedelta(days=30),
            offer_date=date.today(),
            status='PENDING'
        )
        
        # Create another student
        other_user = User.objects.create_user(email='other@test.com', password='testpassword', role=UserRole.STUDENT)
        other_student = Student.objects.create(
            user=other_user, enrollment_number="ENR002", branch="CSE", year=4, semester=8, cgpa=8.5
        )
        
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(f"{self.url}{offer.id}/respond/", {'status': 'ACCEPTED'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # Because of get_queryset

    def test_already_accepted_offer_cannot_be_changed(self):
        offer = Offer.objects.create(
            application=self.application,
            student=self.student,
            company=self.company,
            placement_drive=self.drive,
            offer_type='FULL_TIME',
            job_title='SDE',
            package_lpa='10.50',
            joining_location='Bangalore',
            joining_date=date.today() + timedelta(days=30),
            offer_date=date.today(),
            status='ACCEPTED'
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.patch(f"{self.url}{offer.id}/respond/", {'status': 'REJECTED'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot respond to an offer that is already", str(response.data))

    def test_already_rejected_offer_cannot_be_changed(self):
        offer = Offer.objects.create(
            application=self.application,
            student=self.student,
            company=self.company,
            placement_drive=self.drive,
            offer_type='FULL_TIME',
            job_title='SDE',
            package_lpa='10.50',
            joining_location='Bangalore',
            joining_date=date.today() + timedelta(days=30),
            offer_date=date.today(),
            status='REJECTED'
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.patch(f"{self.url}{offer.id}/respond/", {'status': 'ACCEPTED'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cannot respond to an offer that is already", str(response.data))

    def test_my_offers(self):
        Offer.objects.create(
            application=self.application, student=self.student, company=self.company,
            placement_drive=self.drive, offer_type='FULL_TIME', job_title='SDE',
            package_lpa='10.50', joining_location='Bangalore', joining_date=date.today(),
            offer_date=date.today(), status='PENDING'
        )
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f"{self.url}my-offers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_my_offers_permissions(self):
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.get(f"{self.url}my-offers/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accepted_offers(self):
        Offer.objects.create(
            application=self.application, student=self.student, company=self.company,
            placement_drive=self.drive, offer_type='FULL_TIME', job_title='SDE',
            package_lpa='10.50', joining_location='Bangalore', joining_date=date.today(),
            offer_date=date.today(), status='ACCEPTED'
        )
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.get(f"{self.url}accepted/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_accepted_offers_permissions(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f"{self.url}accepted/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filtering(self):
        Offer.objects.create(
            application=self.application, student=self.student, company=self.company,
            placement_drive=self.drive, offer_type='FULL_TIME', job_title='SDE',
            package_lpa='10.50', joining_location='Bangalore', joining_date=date.today(),
            offer_date=date.today(), status='PENDING'
        )
        self.client.force_authenticate(user=self.officer_user)
        
        # Test company filter
        response = self.client.get(f"{self.url}?company={self.company.id}")
        self.assertEqual(len(response.data), 1)
        
        response = self.client.get(f"{self.url}?company=999")
        self.assertEqual(len(response.data), 0)

        # Test status filter
        response = self.client.get(f"{self.url}?status=PENDING")
        self.assertEqual(len(response.data), 1)
        
        response = self.client.get(f"{self.url}?status=ACCEPTED")
        self.assertEqual(len(response.data), 0)

    def test_ordering(self):
        Offer.objects.create(
            application=self.application, student=self.student, company=self.company,
            placement_drive=self.drive, offer_type='FULL_TIME', job_title='SDE1',
            package_lpa='10.50', joining_location='Bangalore', joining_date=date.today(),
            offer_date=date.today(), status='PENDING'
        )
        Offer.objects.create(
            application=self.application, student=self.student, company=self.company,
            placement_drive=self.drive, offer_type='FULL_TIME', job_title='SDE2',
            package_lpa='12.50', joining_location='Bangalore', joining_date=date.today(),
            offer_date=date.today(), status='REJECTED' # We use rejected so unique constraint isn't violated
        )
        
        self.client.force_authenticate(user=self.officer_user)
        response = self.client.get(f"{self.url}?ordering=-package_lpa")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data[0]['package_lpa']), 12.50)
        self.assertEqual(float(response.data[1]['package_lpa']), 10.50)

    def test_placement_status(self):
        Offer.objects.create(
            application=self.application, student=self.student, company=self.company,
            placement_drive=self.drive, offer_type='FULL_TIME', job_title='SDE',
            package_lpa='10.50', joining_location='Bangalore', joining_date=date.today(),
            offer_date=date.today(), status='ACCEPTED'
        )
        self.student.is_placed = True
        self.student.save()
        
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(f"{self.url}placement-status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_placed'])
        self.assertEqual(response.data['total_offers'], 1)
        self.assertEqual(response.data['accepted_offers'], 1)
        self.assertEqual(response.data['rejected_offers'], 0)

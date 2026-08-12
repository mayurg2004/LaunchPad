from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User, UserRole
from .models import Notification

class NotificationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email='user1@test.com', password='password', role=UserRole.STUDENT)
        self.user2 = User.objects.create_user(email='user2@test.com', password='password', role=UserRole.STUDENT)
        
        self.notification1 = Notification.objects.create(
            recipient=self.user1,
            title='Test 1',
            message='Message 1',
            notification_type='SYSTEM',
            is_read=False
        )
        self.notification2 = Notification.objects.create(
            recipient=self.user1,
            title='Test 2',
            message='Message 2',
            notification_type='OFFER',
            is_read=True
        )
        self.notification_user2 = Notification.objects.create(
            recipient=self.user2,
            title='Test User 2',
            message='Message for user 2',
            notification_type='INTERVIEW',
            is_read=False
        )
        
        self.url = '/api/notifications/'

    def test_notification_creation_in_db(self):
        self.assertEqual(Notification.objects.count(), 3)
        self.assertEqual(self.notification1.title, 'Test 1')

    def test_user_can_view_own_notification(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return 2 notifications for user1
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 2)
        
        response_detail = self.client.get(f"{self.url}{self.notification1.id}/")
        self.assertEqual(response_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(response_detail.data['title'], 'Test 1')

    def test_user_cannot_view_another_users_notification(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"{self.url}{self.notification_user2.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unread_notification_filtering(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"{self.url}unread/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.notification1.id)

    def test_marking_notification_as_read(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(f"{self.url}{self.notification1.id}/", {'is_read': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_deleting_own_notification(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f"{self.url}{self.notification1.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.filter(recipient=self.user1).count(), 1)

    def test_mark_notification_as_read_action(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(f"{self.url}{self.notification1.id}/read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_mark_all_as_read(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.patch(f"{self.url}read-all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
        self.assertEqual(Notification.objects.filter(recipient=self.user1, is_read=False).count(), 0)

    def test_notification_summary(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"{self.url}summary/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_notifications'], 2)
        self.assertEqual(response.data['unread_notifications'], 1)
        self.assertEqual(response.data['read_notifications'], 1)

    def test_filtering_and_ordering(self):
        self.client.force_authenticate(user=self.user1)
        # Test filtering by notification_type
        response = self.client.get(f"{self.url}?notification_type=SYSTEM")
        self.assertEqual(len(response.data['results']), 1)
        
        # Test filtering by is_read
        response = self.client.get(f"{self.url}?is_read=True")
        self.assertEqual(len(response.data['results']), 1)
        
        # Test ordering
        response = self.client.get(f"{self.url}?ordering=created_at")
        self.assertEqual(response.data['results'][0]['id'], self.notification1.id)

    def test_pagination(self):
        # Create enough notifications to trigger pagination
        for i in range(12):
            Notification.objects.create(recipient=self.user1, title=f"Paginate {i}", message="Msg", notification_type="SYSTEM")
            
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data)
        self.assertEqual(len(response.data['results']), 10)

    def test_permissions_read_action(self):
        self.client.force_authenticate(user=self.user1)
        # Try to read user2's notification
        response = self.client.patch(f"{self.url}{self.notification_user2.id}/read/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

from applications.models import Application
from placement_drive.models import PlacementDrive
from companies.models import Company
from students.models import Student
from interviews.models import Interview
from offers.models import Offer
from django.utils import timezone
from datetime import timedelta, date

class NotificationTriggersTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='student@test.com', password='password', role=UserRole.STUDENT)
        self.student = Student.objects.create(
            user=self.user, enrollment_number="ENR123", branch="CSE", year=4, semester=8, cgpa=8.5
        )
        self.company = Company.objects.create(company_name="Tech Corp")
        self.drive = PlacementDrive.objects.create(
            company=self.company, title="SDE Hiring", job_role="SDE", status="OPEN",
            application_deadline=timezone.now() + timedelta(days=2), minimum_cgpa=7.0, eligible_branch="CSE"
        )
        # Clear any notifications created so far (none should exist yet, but to be safe)
        Notification.objects.all().delete()

    def test_application_submitted_notification(self):
        Application.objects.create(student=self.student, placement_drive=self.drive)
        self.assertTrue(Notification.objects.filter(
            recipient=self.user, title="Application Submitted", notification_type="APPLICATION"
        ).exists())

    def test_application_shortlisted_notification(self):
        app = Application.objects.create(student=self.student, placement_drive=self.drive)
        Notification.objects.all().delete() # clear submit notification
        
        app.status = 'SHORTLISTED'
        app.save()
        self.assertTrue(Notification.objects.filter(
            recipient=self.user, title="Application Shortlisted", notification_type="APPLICATION"
        ).exists())

    def test_application_rejected_notification(self):
        app = Application.objects.create(student=self.student, placement_drive=self.drive)
        Notification.objects.all().delete() # clear submit notification
        
        app.status = 'REJECTED'
        app.save()
        self.assertTrue(Notification.objects.filter(
            recipient=self.user, title="Application Update", notification_type="APPLICATION"
        ).exists())

    def test_interview_scheduled_notification(self):
        app = Application.objects.create(student=self.student, placement_drive=self.drive)
        Notification.objects.all().delete()
        
        Interview.objects.create(
            application=app, round_name="Round 1", round_type="TECHNICAL",
            scheduled_at=timezone.now() + timedelta(days=1)
        )
        self.assertTrue(Notification.objects.filter(
            recipient=self.user, title="Interview Scheduled", notification_type="INTERVIEW"
        ).exists())

    def test_interview_passed_notification(self):
        app = Application.objects.create(student=self.student, placement_drive=self.drive)
        interview = Interview.objects.create(
            application=app, round_name="Round 1", round_type="TECHNICAL",
            scheduled_at=timezone.now() + timedelta(days=1), status='COMPLETED'
        )
        Notification.objects.all().delete()
        
        interview.result = 'PASSED'
        interview.save()
        self.assertTrue(Notification.objects.filter(
            recipient=self.user, title="Interview Passed", notification_type="INTERVIEW"
        ).exists())

    def test_interview_failed_notification(self):
        app = Application.objects.create(student=self.student, placement_drive=self.drive)
        interview = Interview.objects.create(
            application=app, round_name="Round 1", round_type="TECHNICAL",
            scheduled_at=timezone.now() + timedelta(days=1), status='COMPLETED'
        )
        Notification.objects.all().delete()
        
        interview.result = 'FAILED'
        interview.save()
        self.assertTrue(Notification.objects.filter(
            recipient=self.user, title="Interview Update", notification_type="INTERVIEW"
        ).exists())

    def test_offer_received_notification(self):
        app = Application.objects.create(student=self.student, placement_drive=self.drive)
        Notification.objects.all().delete()
        
        Offer.objects.create(
            application=app, student=self.student, company=self.company,
            placement_drive=self.drive, offer_type='FULL_TIME', job_title='SDE',
            package_lpa='10.50', joining_location='Bangalore', joining_date=date.today(),
            offer_date=date.today(), status='PENDING'
        )
        self.assertTrue(Notification.objects.filter(
            recipient=self.user, title="New Offer Received", notification_type="OFFER"
        ).exists())

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

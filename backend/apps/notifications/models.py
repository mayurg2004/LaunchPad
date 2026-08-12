from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('PLACEMENT_DRIVE', 'Placement Drive'),
        ('APPLICATION', 'Application'),
        ('INTERVIEW', 'Interview'),
        ('OFFER', 'Offer'),
        ('SYSTEM', 'System'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.email} - {self.title}"

class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preference')
    placement_drive_notifications = models.BooleanField(default=True)
    application_notifications = models.BooleanField(default=True)
    interview_notifications = models.BooleanField(default=True)
    offer_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Preferences"

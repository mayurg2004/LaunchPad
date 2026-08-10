from django.db import models
from applications.models import Application

class Interview(models.Model):
    ROUND_TYPE_CHOICES = [
        ('APTITUDE', 'Aptitude'),
        ('CODING', 'Coding'),
        ('TECHNICAL', 'Technical'),
        ('HR', 'HR'),
        ('MANAGERIAL', 'Managerial'),
        ('FINAL', 'Final'),
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    RESULT_CHOICES = [
        ('PENDING', 'Pending'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    round_name = models.CharField(max_length=255)
    round_type = models.CharField(max_length=20, choices=ROUND_TYPE_CHOICES)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    
    location = models.CharField(max_length=255, blank=True)
    meeting_link = models.URLField(blank=True)
    
    interviewer_name = models.CharField(max_length=255, blank=True)
    interviewer_email = models.EmailField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    feedback = models.TextField(blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application.student.user.email} - {self.round_name}"

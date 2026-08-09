from django.db import models
from students.models import Student
from placement_drive.models import PlacementDrive

class Application(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
        ('SELECTED', 'Selected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='applications')
    placement_drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='APPLIED')
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'placement_drive'], name='unique_student_application')
        ]
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.user.email} - {self.placement_drive.title}"

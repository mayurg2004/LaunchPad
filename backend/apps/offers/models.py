from django.db import models
from applications.models import Application
from students.models import Student
from companies.models import Company
from placement_drive.models import PlacementDrive

class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('INTERNSHIP', 'Internship'),
        ('INTERNSHIP_TO_FULL_TIME', 'Internship to Full Time'),
    ]

    OFFER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='offers')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='offers')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='offers')
    placement_drive = models.ForeignKey(PlacementDrive, on_delete=models.CASCADE, related_name='offers')
    
    offer_type = models.CharField(max_length=50, choices=OFFER_TYPE_CHOICES)
    job_title = models.CharField(max_length=255)
    package_lpa = models.DecimalField(max_digits=10, decimal_places=2)
    joining_location = models.CharField(max_length=255)
    joining_date = models.DateField()
    offer_date = models.DateField()
    offer_letter = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=OFFER_STATUS_CHOICES, default='PENDING')
    remarks = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['application'],
                condition=models.Q(status__in=['PENDING', 'ACCEPTED']),
                name='unique_active_offer_per_application'
            )
        ]

    def __str__(self):
        return f"{self.student.user.email} - {self.company.company_name} ({self.job_title})"

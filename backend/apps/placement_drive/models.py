from django.db import models
from companies.models import Company

class PlacementDrive(models.Model):
    DRIVE_STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='placement_drives')
    title = models.CharField(max_length=255)
    job_role = models.CharField(max_length=255)
    job_description = models.TextField(blank=True)
    package_lpa = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    minimum_cgpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    eligible_branch = models.CharField(max_length=255, blank=True, help_text="E.g., CSE, ISE, ECE or All")
    application_deadline = models.DateTimeField(null=True, blank=True)
    drive_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=DRIVE_STATUS_CHOICES, default='UPCOMING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.company_name} - {self.title}"

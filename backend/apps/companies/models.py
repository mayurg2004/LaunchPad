from django.db import models

class Company(models.Model):
    COMPANY_TYPE_CHOICES = [
        ('SERVICE', 'Service'),
        ('PRODUCT', 'Product'),
        ('STARTUP', 'Startup'),
        ('GOVERNMENT', 'Government'),
    ]

    company_name = models.CharField(max_length=255, unique=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    
    # HR / Contact info
    hr_name = models.CharField(max_length=255, blank=True)
    hr_email = models.EmailField(blank=True)
    hr_contact = models.CharField(max_length=50, blank=True)
    
    industry = models.CharField(max_length=100, blank=True)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPE_CHOICES, blank=True)
    description = models.TextField(blank=True)
    
    headquarters = models.CharField(max_length=255, blank=True)
    locations = models.TextField(blank=True, help_text="Comma-separated list of office locations")
    established_year = models.PositiveIntegerField(null=True, blank=True)
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    linkedin_url = models.URLField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

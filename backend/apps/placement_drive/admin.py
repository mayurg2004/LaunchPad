from django.contrib import admin
from .models import PlacementDrive

@admin.register(PlacementDrive)
class PlacementDriveAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_role', 'package_lpa', 'status', 'drive_date')
    list_filter = ('status', 'company', 'drive_date')
    search_fields = ('title', 'company__company_name', 'job_role')

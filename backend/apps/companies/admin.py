from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'industry', 'company_type', 'is_active', 'established_year')
    list_filter = ('industry', 'company_type', 'is_active')
    search_fields = ('company_name', 'hr_name', 'hr_email', 'industry')
    ordering = ('-created_at',)

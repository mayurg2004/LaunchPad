from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'placement_drive', 'get_company', 'status', 'applied_at')
    list_filter = ('status', 'placement_drive__company', 'applied_at')
    search_fields = ('student__enrollment_number', 'student__user__first_name', 'student__user__last_name', 'placement_drive__title', 'placement_drive__company__company_name')
    ordering = ('-applied_at',)
    readonly_fields = ('applied_at', 'updated_at')

    def get_company(self, obj):
        return obj.placement_drive.company.company_name
    get_company.short_description = 'Company'
    get_company.admin_order_field = 'placement_drive__company__company_name'

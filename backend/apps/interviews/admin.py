from django.contrib import admin
from .models import Interview

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'round_name', 'round_type', 'scheduled_at', 'status', 'result')
    list_filter = ('round_type', 'status', 'result')
    search_fields = ('application__student__user__first_name', 'application__student__user__last_name', 'application__placement_drive__company__company_name')

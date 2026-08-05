from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_number', 'user', 'branch', 'year', 'cgpa', 'is_placed')
    list_filter = ('branch', 'year', 'is_placed', 'gender')
    search_fields = ('enrollment_number', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)

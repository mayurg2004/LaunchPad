from django.contrib import admin
from .models import Resume, ResumeAnalysis

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'is_active', 'uploaded_at')
    list_filter = ('is_active', 'uploaded_at')
    search_fields = ('student__user__email', 'student__enrollment_number', 'title')
    ordering = ('-uploaded_at',)

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'score', 'analyzed_at')
    list_filter = ('analyzed_at', 'score')
    search_fields = ('resume__title', 'resume__student__user__email')
    ordering = ('-analyzed_at',)

from django.contrib import admin
from .models import CareerRecommendation

@admin.register(CareerRecommendation)
class CareerRecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'recommended_role', 'match_score', 'created_at')
    search_fields = ('student__user__email', 'recommended_role')
    list_filter = ('created_at',)


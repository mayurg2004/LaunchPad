from django.contrib import admin
from .models import Offer

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'application', 'student', 'company', 'offer_type', 'status', 'package_lpa', 'offer_date')
    list_filter = ('status', 'offer_type', 'company')
    search_fields = ('student__user__email', 'company__company_name', 'job_title')
    readonly_fields = ('created_at', 'updated_at')

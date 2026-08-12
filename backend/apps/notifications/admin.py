from django.contrib import admin
from .models import Notification, NotificationPreference

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'recipient__username', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'placement_drive_notifications', 'application_notifications', 'interview_notifications', 'offer_notifications', 'system_notifications')
    search_fields = ('user__email', 'user__username')

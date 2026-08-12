from rest_framework import serializers
from .models import Notification, NotificationPreference

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at', 'recipient']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

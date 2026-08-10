from rest_framework import serializers
from django.utils import timezone
from .models import Interview
from applications.models import Application

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # Basic validation: scheduled_at must be in the future for new interviews
        if not self.instance:
            if 'scheduled_at' in data and data['scheduled_at'] < timezone.now():
                raise serializers.ValidationError({"scheduled_at": "Scheduled time must be in the future."})
        else:
            # If updating and changing scheduled_at, ensure it's valid
            if 'scheduled_at' in data and data['scheduled_at'] != self.instance.scheduled_at:
                if data['scheduled_at'] < timezone.now():
                    raise serializers.ValidationError({"scheduled_at": "Scheduled time must be in the future."})
                    
        return data

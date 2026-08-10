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

class InterviewStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['status']
        
    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Interview.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid status provided.")
        return value

class InterviewResultUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['result']
        
    def validate_result(self, value):
        valid_results = [choice[0] for choice in Interview.RESULT_CHOICES]
        if value not in valid_results:
            raise serializers.ValidationError("Invalid result provided.")
        return value

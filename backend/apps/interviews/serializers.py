from rest_framework import serializers
from django.utils import timezone
from .models import Interview
from applications.models import Application

class InterviewSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='application.placement_drive.company.company_name', read_only=True)
    job_role = serializers.CharField(source='application.placement_drive.job_role', read_only=True)
    placement_drive_title = serializers.CharField(source='application.placement_drive.title', read_only=True)
    student_name = serializers.SerializerMethodField()
    student_enrollment_number = serializers.CharField(source='application.student.enrollment_number', read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'round_name', 'round_type', 'scheduled_at', 
            'duration_minutes', 'location', 'meeting_link', 'interviewer_name', 
            'interviewer_email', 'status', 'feedback', 'result', 'created_at', 
            'updated_at', 'company_name', 'job_role', 'placement_drive_title', 
            'student_name', 'student_enrollment_number'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_student_name(self, obj):
        return f"{obj.application.student.user.first_name} {obj.application.student.user.last_name}".strip()

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

from rest_framework import serializers
from .models import Resume, ResumeAnalysis

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'student', 'title', 'version_number', 'file', 'is_active', 'uploaded_at', 'updated_at']
        read_only_fields = ['id', 'student', 'version_number', 'uploaded_at', 'updated_at']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title must not be empty.")
        return value

class ResumeAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysis
        fields = ['id', 'resume', 'score', 'skills_found', 'strengths', 'weaknesses', 'suggestions', 'analyzed_at']
        read_only_fields = ['id', 'resume', 'analyzed_at']

from rest_framework import serializers
from .models import Student
from django.core.validators import MinValueValidator, MaxValueValidator

class StudentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'email', 'first_name', 'last_name',
            'enrollment_number', 'branch', 'year', 'semester',
            'cgpa', 'phone_number', 'gender', 'date_of_birth',
            'skills', 'github_url', 'linkedin_url', 'portfolio_url',
            'resume', 'profile_photo', 'is_placed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'is_placed']

    def validate_cgpa(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError("CGPA must be between 0 and 10.")
        return value

    def validate_year(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Year must be between 1 and 5.")
        return value

    def validate_semester(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Semester must be between 1 and 10.")
        return value

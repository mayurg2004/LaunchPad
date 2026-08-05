from rest_framework import serializers
from .models import Company
from datetime import date

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_established_year(self, value):
        current_year = date.today().year
        if value and (value < 1800 or value > current_year):
            raise serializers.ValidationError(f"Established year must be between 1800 and {current_year}.")
        return value

    def validate_employee_count(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Employee count must be at least 1.")
        return value

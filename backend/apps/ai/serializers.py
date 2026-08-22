from rest_framework import serializers
from .models import CareerRecommendation

class CareerRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerRecommendation
        fields = '__all__'
        read_only_fields = ['student', 'created_at', 'updated_at']

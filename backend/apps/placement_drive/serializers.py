from rest_framework import serializers
from .models import PlacementDrive

class PlacementDriveSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    
    class Meta:
        model = PlacementDrive
        fields = '__all__'

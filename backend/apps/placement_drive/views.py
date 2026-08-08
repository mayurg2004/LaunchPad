from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import PlacementDrive
from .serializers import PlacementDriveSerializer

class PlacementDriveViewSet(viewsets.ModelViewSet):
    queryset = PlacementDrive.objects.all().order_by('-created_at')
    serializer_class = PlacementDriveSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return super().get_queryset()

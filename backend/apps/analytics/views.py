from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from accounts.models import UserRole
from students.models import Student
from companies.models import Company
from placement_drive.models import PlacementDrive
from applications.models import Application
from interviews.models import Interview
from offers.models import Offer

class IsAdminOrPlacementOfficer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.ADMIN, UserRole.PLACEMENT_OFFICER]
        )

class AnalyticsOverviewView(APIView):
    permission_classes = [IsAdminOrPlacementOfficer]

    def get(self, request):
        total_students = Student.objects.count()
        total_companies = Company.objects.count()
        total_placement_drives = PlacementDrive.objects.count()
        total_applications = Application.objects.count()
        total_interviews = Interview.objects.count()
        total_offers = Offer.objects.count()
        
        placed_students = Student.objects.filter(is_placed=True).count()
        
        if total_students > 0:
            placement_percentage = round((placed_students / total_students) * 100, 2)
        else:
            placement_percentage = 0.0

        return Response({
            "total_students": total_students,
            "total_companies": total_companies,
            "total_placement_drives": total_placement_drives,
            "total_applications": total_applications,
            "total_interviews": total_interviews,
            "total_offers": total_offers,
            "placed_students": placed_students,
            "placement_percentage": placement_percentage
        })

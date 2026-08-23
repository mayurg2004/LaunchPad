from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from accounts.models import UserRole
from students.models import Student
from companies.models import Company
from placement_drive.models import PlacementDrive
from applications.models import Application
from interviews.models import Interview
from offers.models import Offer
from .services import DashboardService

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

class DashboardSummaryView(APIView):
    permission_classes = [IsAdminOrPlacementOfficer]

    def get(self, request):
        summary = DashboardService.get_summary()
        return Response(summary, status=status.HTTP_200_OK)

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

class DepartmentAnalyticsView(APIView):
    permission_classes = [IsAdminOrPlacementOfficer]

    def get(self, request):
        from django.db.models import Count, Q
        
        departments_data = Student.objects.values('branch').annotate(
            total_students=Count('id'),
            placed_students=Count('id', filter=Q(is_placed=True))
        )

        response_data = []
        for dept in departments_data:
            total = dept['total_students']
            placed = dept['placed_students']
            percentage = round((placed / total) * 100, 2) if total > 0 else 0.0

            response_data.append({
                "branch": dept['branch'],
                "total_students": total,
                "placed_students": placed,
                "placement_percentage": percentage
            })

        response_data.sort(key=lambda x: x['placement_percentage'], reverse=True)

        return Response(response_data)

class CompanyAnalyticsView(APIView):
    permission_classes = [IsAdminOrPlacementOfficer]

    def get(self, request):
        from django.db.models import Count, Q, Avg

        companies_data = Company.objects.annotate(
            total_applications=Count('placement_drives__applications', distinct=True),
            shortlisted_applications=Count('placement_drives__applications', filter=Q(placement_drives__applications__status='SHORTLISTED'), distinct=True),
            selected_applications=Count('placement_drives__applications', filter=Q(placement_drives__applications__status='SELECTED'), distinct=True),
            total_offers=Count('offers', distinct=True),
            average_package_lpa=Avg('offers__package_lpa')
        )

        response_data = []
        for company in companies_data:
            avg_pkg = company.average_package_lpa
            response_data.append({
                "company_name": company.company_name,
                "total_applications": company.total_applications,
                "shortlisted_applications": company.shortlisted_applications,
                "selected_applications": company.selected_applications,
                "total_offers": company.total_offers,
                "average_package_lpa": round(avg_pkg, 2) if avg_pkg is not None else 0.0
            })

        response_data.sort(key=lambda x: x['total_offers'], reverse=True)

        return Response(response_data)


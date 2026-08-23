from students.models import Student
from companies.models import Company
from placement_drive.models import PlacementDrive
from applications.models import Application
from interviews.models import Interview
from offers.models import Offer

class DashboardService:
    @staticmethod
    def get_summary():
        total_students = Student.objects.count()
        total_companies = Company.objects.count()
        active_placement_drives = PlacementDrive.objects.filter(status='OPEN').count()
        total_applications = Application.objects.count()
        shortlisted_applications = Application.objects.filter(status='SHORTLISTED').count()
        selected_applications = Application.objects.filter(status='SELECTED').count()
        scheduled_interviews = Interview.objects.filter(status='SCHEDULED').count()
        total_offers = Offer.objects.count()
        accepted_offers = Offer.objects.filter(status='ACCEPTED').count()
        
        placed_students = Student.objects.filter(is_placed=True).count()
        
        placement_percentage = 0.0
        if total_students > 0:
            placement_percentage = round((placed_students / total_students) * 100, 2)
            
        return {
            "total_students": total_students,
            "total_companies": total_companies,
            "active_placement_drives": active_placement_drives,
            "total_applications": total_applications,
            "shortlisted_applications": shortlisted_applications,
            "selected_applications": selected_applications,
            "scheduled_interviews": scheduled_interviews,
            "total_offers": total_offers,
            "accepted_offers": accepted_offers,
            "placed_students": placed_students,
            "placement_percentage": placement_percentage
        }

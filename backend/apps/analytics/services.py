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

    @staticmethod
    def get_recent_activity(limit=50):
        activities = []
        
        apps = Application.objects.select_related('student__user', 'placement_drive__company').order_by('-applied_at')[:limit]
        for app in apps:
            activities.append({
                "activity_type": "APPLICATION",
                "description": f"Applied for {app.placement_drive.title}",
                "related_company": app.placement_drive.company.company_name,
                "student_name": f"{app.student.user.first_name} {app.student.user.last_name}".strip(),
                "timestamp": app.applied_at
            })
            
        interviews = Interview.objects.select_related('application__student__user', 'application__placement_drive__company').order_by('-created_at')[:limit]
        for interview in interviews:
            activities.append({
                "activity_type": "INTERVIEW",
                "description": f"Interview scheduled: {interview.round_name}",
                "related_company": interview.application.placement_drive.company.company_name,
                "student_name": f"{interview.application.student.user.first_name} {interview.application.student.user.last_name}".strip(),
                "timestamp": interview.created_at
            })
            
        offers = Offer.objects.select_related('student__user', 'company').order_by('-created_at')[:limit]
        for offer in offers:
            activities.append({
                "activity_type": "OFFER",
                "description": f"Offer extended: {offer.job_title} ({offer.package_lpa} LPA)",
                "related_company": offer.company.company_name,
                "student_name": f"{offer.student.user.first_name} {offer.student.user.last_name}".strip(),
                "timestamp": offer.created_at
            })
            
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]

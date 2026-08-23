from typing import Dict, Any, List
from django.conf import settings
from .providers import get_provider, AIProvider

class AIService:
    """
    Service layer for AI operations.
    Acts as an intermediary between Django application code and AI providers.
    """
    
    def __init__(self, provider_name: str = None):
        if provider_name is None:
            provider_name = getattr(settings, 'AI_PROVIDER', 'mock')
        self.provider: AIProvider = get_provider(provider_name)
        
    def analyze_resume(self, text: str) -> Dict[str, Any]:
        return self.provider.analyze_resume(text)
        
    def generate_resume_suggestions(self, text: str, skills: List[str]) -> Dict[str, Any]:
        return self.provider.generate_resume_suggestions(text, skills)
        
    def analyze_skill_gap(self, resume_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        return self.provider.analyze_skill_gap(resume_skills, required_skills)
        
    def generate_career_recommendations(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self.provider.generate_career_recommendations(profile_data)

    def get_recommended_drives(self, student) -> tuple[Dict[str, Any], int]:
        from placement_drive.models import PlacementDrive
        from resumes.models import Resume, ResumeAnalysis

        active_resume = Resume.objects.filter(student=student, is_active=True).first()
        if not active_resume:
            return {"error": "No active resume found."}, 400

        latest_analysis = ResumeAnalysis.objects.filter(resume=active_resume).order_by('-analyzed_at').first()
        if not latest_analysis:
            return {"error": "No resume analysis found. Please analyze your resume first."}, 400

        student_skills = {s.lower().strip() for s in latest_analysis.skills_found}

        open_drives = PlacementDrive.objects.filter(status='OPEN')
        recommendations = []

        for drive in open_drives:
            if not drive.required_skills:
                continue

            required_skills = {s.lower().strip() for s in drive.required_skills}
            if not required_skills:
                continue

            matched_skills = student_skills.intersection(required_skills)
            missing_skills = required_skills - student_skills

            match_percentage = (len(matched_skills) / len(required_skills)) * 100

            if match_percentage > 0:
                recommendations.append({
                    "placement_drive_id": drive.id,
                    "company_name": drive.company.company_name,
                    "job_role": drive.job_role,
                    "package_lpa": drive.package_lpa,
                    "required_skills": list(required_skills),
                    "matched_skills": list(matched_skills),
                    "missing_skills": list(missing_skills),
                    "match_percentage": round(match_percentage, 2)
                })

        recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)

        if not recommendations:
            return {"error": "No matching drives found at this time."}, 404

        return {"data": recommendations}, 200

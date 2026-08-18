from typing import Dict, Any, List
from .base import AIProvider

class MockAIProvider(AIProvider):
    """
    A mock provider that returns placeholder responses.
    Used for testing and when no external provider is configured.
    """
    
    def analyze_resume(self, text: str) -> Dict[str, Any]:
        return {
            "status": "success",
            "provider": "mock",
            "message": "This is a placeholder response for analyze_resume."
        }
        
    def generate_resume_suggestions(self, text: str, skills: List[str]) -> Dict[str, Any]:
        return {
            "status": "success",
            "provider": "mock",
            "suggestions": ["Consider adding a mock projects section.", "Consider adding mock contact details."]
        }
        
    def analyze_skill_gap(self, resume_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        return {
            "status": "success",
            "provider": "mock",
            "missing_skills": [s for s in required_skills if s not in resume_skills]
        }
        
    def generate_career_recommendations(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {"role": "Mock Software Engineer", "match_score": 95},
            {"role": "Mock Data Scientist", "match_score": 80}
        ]

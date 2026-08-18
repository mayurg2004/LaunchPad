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

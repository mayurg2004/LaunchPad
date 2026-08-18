from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    """
    Abstract base class for all AI providers.
    Ensures that any provider implements the necessary methods.
    """
    
    @abstractmethod
    def analyze_resume(self, text: str) -> Dict[str, Any]:
        """Analyze a resume and return a structured response."""
        pass
        
    @abstractmethod
    def generate_resume_suggestions(self, text: str, skills: List[str]) -> Dict[str, Any]:
        """Generate improvement suggestions for a resume."""
        pass
        
    @abstractmethod
    def analyze_skill_gap(self, resume_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        """Analyze the skill gap between a resume and job requirements."""
        pass
        
    @abstractmethod
    def generate_career_recommendations(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate career recommendations based on student profile."""
        pass

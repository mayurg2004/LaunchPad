from django.test import TestCase
from django.conf import settings
from .services import AIService
from .providers.mock import MockAIProvider

class AIServiceTests(TestCase):
    def test_ai_service_instantiation(self):
        """Test that AIService can be instantiated."""
        service = AIService()
        self.assertIsNotNone(service)
        self.assertIsInstance(service.provider, MockAIProvider)
        
    def test_provider_abstraction(self):
        """Test that the service uses the correct provider based on config."""
        service = AIService(provider_name='mock')
        self.assertIsInstance(service.provider, MockAIProvider)
        
        # Test default fallback when an unknown provider is requested
        service_unknown = AIService(provider_name='unknown')
        self.assertIsInstance(service_unknown.provider, MockAIProvider)

    def test_missing_configuration_handled_cleanly(self):
        """Test that when config is missing or using default, it falls back cleanly."""
        # Force default settings behavior (as if AI_PROVIDER is not set)
        original_provider = getattr(settings, 'AI_PROVIDER', None)
        settings.AI_PROVIDER = 'mock'
        
        service = AIService()
        self.assertIsInstance(service.provider, MockAIProvider)
        
        if original_provider:
            settings.AI_PROVIDER = original_provider

    def test_placeholder_analysis_response_structure(self):
        """Test that placeholder responses have the expected structure."""
        service = AIService()
        
        # Test analyze_resume
        response = service.analyze_resume("sample text")
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["provider"], "mock")
        self.assertIn("message", response)
        
        # Test generate_resume_suggestions
        suggestions_response = service.generate_resume_suggestions("text", ["Python"])
        self.assertIn("suggestions", suggestions_response)
        
        # Test analyze_skill_gap
        gap_response = service.analyze_skill_gap(["Python"], ["Python", "Django"])
        self.assertIn("missing_skills", gap_response)
        self.assertEqual(gap_response["missing_skills"], ["Django"])
        
        # Test generate_career_recommendations
        career_response = service.generate_career_recommendations({"name": "Test"})
        self.assertTrue(len(career_response) > 0)
        self.assertIn("role", career_response[0])

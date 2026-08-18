from .base import AIProvider
from .mock import MockAIProvider

def get_provider(provider_name: str) -> AIProvider:
    """Factory function to get the appropriate AI provider."""
    # We can add more providers here as they are implemented
    # For example: if provider_name == 'openai': return OpenAIProvider()
    
    if provider_name == 'mock':
        return MockAIProvider()
    
    # Default fallback is mock
    return MockAIProvider()

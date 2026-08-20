import json
import urllib.request
import urllib.error
from django.conf import settings
from typing import Dict, Any, List
from .base import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.api_key = getattr(settings, 'AI_API_KEY', None)
        self.model_name = getattr(settings, 'AI_MODEL_NAME', 'gpt-4o')
        
        if not self.api_key:
            raise ValueError("AI_API_KEY is missing or not configured.")

    def _call_api(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "response_format": {"type": "json_object"}
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                content = result['choices'][0]['message']['content']
                return json.loads(content)
        except urllib.error.HTTPError as e:
            error_message = e.read().decode('utf-8')
            raise ValueError(f"AI Provider HTTP Error: {e.code} - {error_message}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from AI Provider")
        except Exception as e:
            raise ValueError(f"AI Provider Error: {str(e)}")

    def analyze_resume(self, text: str) -> Dict[str, Any]:
        system_prompt = (
            "You are an expert resume reviewer. Analyze the provided resume text and return a JSON object with the following structure exactly:\n"
            "{\n"
            '  "score": <integer from 0 to 100>,\n'
            '  "strengths": [<list of strings>],\n'
            '  "weaknesses": [<list of strings>],\n'
            '  "skills_found": [<list of strings>],\n'
            '  "suggestions": [<list of strings>]\n'
            "}\n"
            "Provide concise and actionable feedback."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Resume Text:\n{text}"}
        ]
        return self._call_api(messages)

    def generate_resume_suggestions(self, text: str, skills: List[str]) -> Dict[str, Any]:
        return {}
        
    def analyze_skill_gap(self, resume_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
        return {}
        
    def generate_career_recommendations(self, profile_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

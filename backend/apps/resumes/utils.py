import io
import pypdf
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_obj):
    """
    Extracts text from a given PDF file object.
    Returns the extracted text, or None if extraction fails.
    """
    try:
        # Read the file content into a bytes buffer
        # This works for both in-memory and disk-based Django File objects
        file_obj.seek(0)
        file_bytes = file_obj.read()
        
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        return text.strip()
    except pypdf.errors.PyPdfError as e:
        logger.error(f"PyPDF Error parsing PDF: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing PDF: {e}")
        return None

import re

PREDEFINED_SKILLS = [
    "Python", "Java", "C", "C++", "JavaScript", "TypeScript",
    "HTML", "CSS", "React", "Angular", "Node.js", "Django", "Flask",
    "Spring Boot", "Flutter", "Dart", "SQL", "MySQL", "PostgreSQL",
    "MongoDB", "Git", "Docker", "AWS", "Linux", "REST API", "Machine Learning"
]

def detect_skills(text):
    """
    Detects skills from PREDEFINED_SKILLS in the given text (case-insensitive).
    Returns a list of detected skills.
    """
    if not text:
        return []
    
    detected = []
    text_lower = text.lower()
    
    for skill in PREDEFINED_SKILLS:
        skill_lower = skill.lower()
        
        # Determine left boundary
        if skill_lower[0].isalnum():
            pattern = r'\b' + re.escape(skill_lower)
        else:
            pattern = r'(?<!\w)' + re.escape(skill_lower)
            
        # Determine right boundary
        if skill_lower[-1].isalnum():
            pattern += r'(?![a-z0-9\+\#])'
        else:
            pattern += r'(?!\w)'
            
        if re.search(pattern, text_lower):
            detected.append(skill)
            
    return detected

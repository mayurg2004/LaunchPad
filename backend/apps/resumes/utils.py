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

def calculate_resume_score(text, skills_found):
    """
    Calculates a basic rule-based resume score from 0 to 100.
    """
    if not text:
        return 0.0
        
    score = 0.0
    text_lower = text.lower()
    
    # 1. Technical skills (up to 40 points)
    # 8 points per skill
    score += min(40, len(skills_found) * 8)
    
    # 2. Resume sections (up to 30 points)
    # 5 points per section
    sections = [
        r'\beducation\b',
        r'\b(experience|work history|employment)\b',
        r'\bprojects\b',
        r'\bskills\b',
        r'\bcertifications\b',
        r'\b(achievements|awards)\b',
        r'\b(contact|profile|about)\b'
    ]
    sections_found = 0
    for pattern in sections:
        if re.search(pattern, text_lower):
            sections_found += 1
    score += min(30, sections_found * 5)
    
    # 3. Contact information (up to 10 points)
    # Email: 5 points, Phone: 5 points
    if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text_lower):
        score += 5
    if re.search(r'\+?\d[\d -]{8,12}\d', text_lower):
        score += 5
        
    # 4. Links (up to 10 points)
    if 'github.com' in text_lower or 'github' in text_lower:
        score += 4
    if 'linkedin.com' in text_lower or 'linkedin' in text_lower:
        score += 4
    if 'portfolio' in text_lower or 'http' in text_lower or 'www.' in text_lower:
        score += 2
        
    # 5. Length/content quality (up to 10 points)
    text_length = len(text)
    if 1000 <= text_length <= 4000:
        score += 10
    elif 500 <= text_length < 1000 or text_length > 4000:
        score += 5
        
    # Clamp between 0 and 100
    return float(max(0, min(100, score)))

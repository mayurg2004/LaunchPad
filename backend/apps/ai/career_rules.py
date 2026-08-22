CAREER_RULES = [
    {
        "role": "Backend Developer",
        "skills": ["Python", "Django", "SQL"]
    },
    {
        "role": "Java Backend Developer",
        "skills": ["Java", "Spring Boot", "SQL"]
    },
    {
        "role": "Frontend Developer",
        "skills": ["JavaScript", "React", "HTML", "CSS"]
    },
    {
        "role": "Flutter Developer",
        "skills": ["Flutter", "Dart"]
    },
    {
        "role": "Machine Learning Engineer",
        "skills": ["Python", "Machine Learning"]
    },
    {
        "role": "DevOps Engineer",
        "skills": ["Docker", "AWS", "Linux"]
    }
]

def generate_rule_based_recommendations(resume_skills):
    """
    Given a list of skills, generates rule-based recommendations.
    """
    resume_skills_lower = [s.lower() for s in (resume_skills or [])]
    recommendations = []
    
    for rule in CAREER_RULES:
        required_skills = rule["skills"]
        matched = []
        missing = []
        
        for req in required_skills:
            if req.lower() in resume_skills_lower:
                matched.append(req)
            else:
                missing.append(req)
        
        match_score = (len(matched) / len(required_skills)) * 100 if required_skills else 0
        
        # We can add all rules and show match score, or filter those with score > 0
        # The prompt says: Calculate a match_score based on how many required skills for the role are present.
        # It's better to only recommend if there is at least some match, or maybe return all. Let's return all, or just those with match_score > 0 to be safe.
        # Actually, let's return all roles evaluated so the student knows where they stand. Or only > 0. Let's do > 0.
        if match_score > 0:
            recommendations.append({
                "role": rule["role"],
                "match_score": round(match_score, 2),
                "matched_skills": matched,
                "missing_skills": missing,
                "explanation": f"You have {len(matched)} out of {len(required_skills)} key skills for {rule['role']}."
            })
            
    return recommendations

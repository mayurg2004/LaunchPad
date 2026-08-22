from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from students.models import Student

class CareerRecommendation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='recommendations')
    recommended_role = models.CharField(max_length=255)
    match_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    explanation = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recommendation for {self.student.user.email}: {self.recommended_role}"

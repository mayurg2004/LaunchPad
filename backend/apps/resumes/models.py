from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

def validate_file_size(value):
    filesize = value.size
    if filesize > 5242880: # 5 MB
        raise ValidationError("The maximum file size that can be uploaded is 5MB")
    return value

class Resume(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='student_resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf']), validate_file_size]
    )
    is_active = models.BooleanField(default=False)
    version_number = models.PositiveIntegerField(default=1, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.student.user.email} - {self.title} (v{self.version_number})"

    def save(self, *args, **kwargs):
        if not self.pk and self.version_number == 1:
            # Calculate next version number if this is a new object
            last_version = Resume.objects.filter(student=self.student).aggregate(models.Max('version_number'))['version_number__max']
            self.version_number = (last_version or 0) + 1
            
        if self.is_active:
            Resume.objects.filter(student=self.student).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

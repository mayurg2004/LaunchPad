from rest_framework import viewsets
from .models import Interview
from .serializers import InterviewSerializer
from .permissions import InterviewPermissions
from accounts.models import UserRole

class InterviewViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewSerializer
    permission_classes = [InterviewPermissions]

    def get_queryset(self):
        user = self.request.user
        queryset = Interview.objects.all().order_by('scheduled_at')

        if not user.is_authenticated:
            return Interview.objects.none()

        if user.role == UserRole.STUDENT:
            if hasattr(user, 'student_profile'):
                queryset = queryset.filter(application__student=user.student_profile)
            else:
                queryset = Interview.objects.none()
        elif user.role == UserRole.RECRUITER:
            if hasattr(user, 'recruiter_profile') and hasattr(user.recruiter_profile, 'company'):
                queryset = queryset.filter(application__placement_drive__company=user.recruiter_profile.company)
            else:
                queryset = Interview.objects.none()
        elif user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            pass

        return queryset

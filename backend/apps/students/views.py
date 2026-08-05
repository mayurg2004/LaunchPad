from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from .models import Student
from .serializers import StudentSerializer
from .permissions import IsStudent, IsPlacementOfficerOrAdmin

class StudentCreateAPIView(generics.CreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsStudent]

    def perform_create(self, serializer):
        if Student.objects.filter(user=self.request.user).exists():
            raise ValidationError("Student profile already exists for this user.")
        serializer.save(user=self.request.user)


class StudentProfileAPIView(generics.RetrieveAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        try:
            return self.request.user.student_profile
        except Student.DoesNotExist:
            raise ValidationError("Student profile not found.")


class StudentProfileUpdateAPIView(generics.UpdateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsStudent]

    def get_object(self):
        try:
            return self.request.user.student_profile
        except Student.DoesNotExist:
            raise ValidationError("Student profile not found.")


class StudentListAPIView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsPlacementOfficerOrAdmin]

    def get_queryset(self):
        queryset = Student.objects.all()
        branch = self.request.query_params.get('branch')
        year = self.request.query_params.get('year')
        cgpa = self.request.query_params.get('cgpa')

        if branch:
            queryset = queryset.filter(branch__iexact=branch)
        if year:
            queryset = queryset.filter(year=year)
        if cgpa:
            queryset = queryset.filter(cgpa__gte=cgpa)

        return queryset

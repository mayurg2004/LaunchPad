from rest_framework import serializers
from django.utils import timezone
from .models import Application
from placement_drive.models import PlacementDrive
from students.models import Student

class ApplicationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_enrollment_number = serializers.CharField(source='student.enrollment_number', read_only=True)
    company_name = serializers.CharField(source='placement_drive.company.company_name', read_only=True)
    placement_drive_title = serializers.CharField(source='placement_drive.title', read_only=True)
    job_role = serializers.CharField(source='placement_drive.job_role', read_only=True)
    package = serializers.DecimalField(source='placement_drive.package_lpa', max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'student', 'placement_drive', 'status', 'applied_at', 'updated_at',
            'student_name', 'student_enrollment_number', 'company_name',
            'placement_drive_title', 'job_role', 'package'
        ]
        read_only_fields = ['status', 'applied_at', 'updated_at', 'student']

    def get_student_name(self, obj):
        return f"{obj.student.user.first_name} {obj.student.user.last_name}".strip()


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['placement_drive']

    def validate(self, data):
        request = self.context.get('request')
        if not hasattr(request.user, 'student_profile'):
            raise serializers.ValidationError("Only students can apply for placement drives.")
            
        student = request.user.student_profile
        placement_drive = data['placement_drive']

        # 1 & 5. Check if already applied (UniqueConstraint handles DB side, but good to catch early)
        if Application.objects.filter(student=student, placement_drive=placement_drive).exists():
            raise serializers.ValidationError("You have already applied to this placement drive.")

        # 2. Check if drive is OPEN
        if placement_drive.status != 'OPEN':
            raise serializers.ValidationError("This placement drive is not open for applications.")

        # 3. Check application deadline
        if placement_drive.application_deadline and placement_drive.application_deadline < timezone.now():
            raise serializers.ValidationError("The application deadline for this drive has passed.")

        # 4. Check eligibility (CGPA)
        if placement_drive.minimum_cgpa and student.cgpa < placement_drive.minimum_cgpa:
            raise serializers.ValidationError(f"Your CGPA ({student.cgpa}) does not meet the minimum requirement ({placement_drive.minimum_cgpa}).")

        # 4. Check eligibility (Branch)
        if placement_drive.eligible_branch:
            eligible_branches = [b.strip().lower() for b in placement_drive.eligible_branch.split(',')]
            if 'all' not in eligible_branches and student.branch.lower() not in eligible_branches:
                raise serializers.ValidationError(f"Your branch ({student.branch}) is not eligible for this drive.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        student = request.user.student_profile
        return Application.objects.create(student=student, placement_drive=validated_data['placement_drive'])


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']

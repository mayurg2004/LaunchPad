from rest_framework import permissions
from accounts.models import UserRole

class InterviewPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            return True
            
        if request.user.role == UserRole.STUDENT:
            # Students can only GET
            return request.method in permissions.SAFE_METHODS
            
        if request.user.role == UserRole.RECRUITER:
             # Recruiters can manage interviews for their company
             return True
             
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            return True
            
        if request.user.role == UserRole.STUDENT:
            if request.method in permissions.SAFE_METHODS:
                return hasattr(request.user, 'student_profile') and obj.application.student == request.user.student_profile
            return False
            
        if request.user.role == UserRole.RECRUITER:
             if hasattr(request.user, 'recruiter_profile') and hasattr(request.user.recruiter_profile, 'company'):
                 return obj.application.placement_drive.company == request.user.recruiter_profile.company
             return False
             
        return False

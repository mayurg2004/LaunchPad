from rest_framework import permissions
from accounts.models import UserRole

class IsResumeOwnerOrAdminOrOfficer(permissions.BasePermission):
    """
    Custom permission for Resume access:
    - Students can only access their own resumes.
    - Placement Officers and Admins can view all resumes.
    - Recruiters cannot access resumes directly (handled by get_queryset).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Only students can upload (create) resumes
        if view.action == 'create':
            return request.user.role == UserRole.STUDENT
            
        return True

    def has_object_permission(self, request, view, obj):
        # Students can access their own resume
        if request.user.role == UserRole.STUDENT:
            return obj.student.user == request.user
            
        # Placement officers and admins have read-only access (or manage if needed)
        # Assuming they only need to view
        if request.user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]:
            if view.action in ['retrieve', 'list']:
                return True
            return False
            
        return False

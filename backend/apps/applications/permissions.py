from rest_framework import permissions
from accounts.models import UserRole

class IsStudentAndOwner(permissions.BasePermission):
    """
    Students can only create and view their own applications.
    They cannot update or delete them.
    """
    def has_permission(self, request, view):
        if request.user.role == UserRole.STUDENT:
            # Can create application (POST) and list their own (handled in get_queryset)
            return request.method in permissions.SAFE_METHODS or request.method == 'POST'
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.STUDENT:
            # Can view their own application
            if request.method in permissions.SAFE_METHODS:
                return hasattr(request.user, 'student_profile') and obj.student == request.user.student_profile
            # Cannot PATCH/PUT/DELETE
            return False
        return False


class IsPlacementOfficerOrAdmin(permissions.BasePermission):
    """
    Placement Officers and Admins can view and manage all applications.
    """
    def has_permission(self, request, view):
        return request.user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]

    def has_object_permission(self, request, view, obj):
        return request.user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]


class IsRecruiterForCompany(permissions.BasePermission):
    """
    Recruiters can only view applications for their company.
    """
    def has_permission(self, request, view):
        if request.user.role == UserRole.RECRUITER:
            return request.method in permissions.SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.RECRUITER and request.method in permissions.SAFE_METHODS:
            # Assuming a Recruiter is linked to a Company via `recruiter_profile.company`
            # This handles the missing Recruiter model safely by returning False if missing
            if hasattr(request.user, 'recruiter_profile') and hasattr(request.user.recruiter_profile, 'company'):
                return obj.placement_drive.company == request.user.recruiter_profile.company
        return False

class ApplicationPermissions(permissions.BasePermission):
    """
    Master permission class combining the roles.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        student_perm = IsStudentAndOwner().has_permission(request, view)
        admin_perm = IsPlacementOfficerOrAdmin().has_permission(request, view)
        recruiter_perm = IsRecruiterForCompany().has_permission(request, view)
        
        return student_perm or admin_perm or recruiter_perm

    def has_object_permission(self, request, view, obj):
        student_perm = IsStudentAndOwner().has_object_permission(request, view, obj)
        admin_perm = IsPlacementOfficerOrAdmin().has_object_permission(request, view, obj)
        recruiter_perm = IsRecruiterForCompany().has_object_permission(request, view, obj)
        
        return student_perm or admin_perm or recruiter_perm

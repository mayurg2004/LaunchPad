from rest_framework import permissions
from accounts.models import UserRole

class IsPlacementOfficerOrAdmin(permissions.BasePermission):
    """
    Placement Officers and Admins can view and manage all offers.
    """
    def has_permission(self, request, view):
        return request.user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]

    def has_object_permission(self, request, view, obj):
        return request.user.role in [UserRole.PLACEMENT_OFFICER, UserRole.ADMIN]

class IsStudentViewer(permissions.BasePermission):
    """
    Students can only view their own offers.
    """
    def has_permission(self, request, view):
        if request.user.role == UserRole.STUDENT:
            return request.method in permissions.SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == UserRole.STUDENT:
            if request.method in permissions.SAFE_METHODS:
                return hasattr(request.user, 'student_profile') and obj.student == request.user.student_profile
        return False

class OfferPermissions(permissions.BasePermission):
    """
    Master permission class combining roles for Offers.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        student_perm = IsStudentViewer().has_permission(request, view)
        admin_perm = IsPlacementOfficerOrAdmin().has_permission(request, view)
        
        return student_perm or admin_perm

    def has_object_permission(self, request, view, obj):
        student_perm = IsStudentViewer().has_object_permission(request, view, obj)
        admin_perm = IsPlacementOfficerOrAdmin().has_object_permission(request, view, obj)
        
        return student_perm or admin_perm

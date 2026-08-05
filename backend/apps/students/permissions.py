from rest_framework import permissions

class IsStudent(permissions.BasePermission):
    """
    Allows access only to users with STUDENT role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'STUDENT')

class IsPlacementOfficerOrAdmin(permissions.BasePermission):
    """
    Allows access to Placement Officers and Admins.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and 
            request.user.role in ['PLACEMENT_OFFICER', 'ADMIN']
        )

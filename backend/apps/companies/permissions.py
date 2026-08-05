from rest_framework import permissions

class IsPlacementOfficerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Placement Officers or Admins to edit or delete.
    Students and Recruiters can only view.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        # Write permissions are only allowed to placement officers and admins.
        return bool(
            request.user and request.user.is_authenticated and 
            request.user.role in ['PLACEMENT_OFFICER', 'ADMIN']
        )

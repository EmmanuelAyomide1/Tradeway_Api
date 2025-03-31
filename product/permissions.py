from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Permission class to allow only admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type == 'ADMIN' 
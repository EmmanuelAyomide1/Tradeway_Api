from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission class to allow only admin users to access the view.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type == 'ADMIN'


class IsSellerOrReadOnly(permissions.BasePermission):
    """"
    Permission class to allow only sellers to access the view.
    """

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.account_type == 'SELLER'


class IsProductSeller(permissions.BasePermission):
    """
    Pernission class to allow only product seller and admins to access the view.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "seller"):
            return obj.seller == request.user or request.user.is_staff
        else:
            return obj.product.seller == request.user or request.user.is_staff


class IsReviewOwnerOrAdminPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff

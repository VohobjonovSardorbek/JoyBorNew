from rest_framework import permissions


class PaymentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user

        return user.role == user.Role.IS_ADMIN

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == 'superadmin':
            return request.method in permissions.SAFE_METHODS

        if user.role == 'admin':
            return True

        return False

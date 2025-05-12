from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_super_admin


class IsDormitoryAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_dormitory_admin


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_student


class IsAuthenticatedOrSuperAdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return request.user and request.user.is_super_admin


class CanCreateDormitoryAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Faqat superadmin yangi admin yaratishi mumkin
        return request.user.is_authenticated and request.user.role == 'superadmin'


class IsSelfOrSuperAdmin(permissions.BasePermission):
    """
    Custom permission to allow users to edit their own profile or allow superadmins to edit any profile.
    """

    def has_object_permission(self, request, view, obj):
        # Allow the owner of the profile or superadmin to edit the profile
        return obj.user == request.user or request.user.is_super_admin



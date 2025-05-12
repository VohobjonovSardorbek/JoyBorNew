from rest_framework import permissions


class IsSuperAdminOrOwner(permissions.BasePermission):
    """
    Superadmin yoki ariza egasi bo'lgan foydalanuvchilar faqat arizani yangilay oladi.
    """

    def has_object_permission(self, request, view, obj):
        # Superadmin bo‘lsa
        if request.user.is_super_admin:
            return True

        # Ariza egasi bo‘lsa
        if request.user == obj.student:
            return True

        # Hech kimga ruxsat berilmaydi
        return False


class IsAdminForDormitory(permissions.BasePermission):
    """
    Admin faqat o‘zining yotoqxonasiga tegishli arizalarni ko‘ra oladi.
    """

    def has_object_permission(self, request, view, obj):
        # Admin bo‘lsa va yotoqxona admini bo‘lsa
        if request.user.is_dormitory_admin:
            if obj.dormitory.admin == request.user:
                return True
            return False

        return False


class IsStudentOrAdminForOwnDormitory(permissions.BasePermission):
    """
    Talaba o‘zining arizasini ko‘ra oladi, admin esa faqat o‘zining yotoqxonasidagi arizalarni ko‘ra oladi.
    """

    def has_object_permission(self, request, view, obj):
        # Talaba o‘zining arizasini ko‘rishi mumkin
        if request.user == obj.student:
            return True

        # Admin bo‘lsa va yotoqxona admini bo‘lsa
        if request.user.is_dormitory_admin and obj.dormitory.admin == request.user:
            return True

        return False

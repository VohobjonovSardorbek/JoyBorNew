from rest_framework import permissions


class DormitoryPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user

        # Foydalanuvchi autentifikatsiyadan o‘tgan bo‘lishi kerak
        if not user.is_authenticated:
            return False

        if user.role == user.Role.IS_ADMIN:
            return True

        if view.action in ['list', 'retrieve']:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role == user.Role.IS_ADMIN:
            return True

        if user.role == user.Role.IS_ADMIN:
            if obj.dormitory.admin == user:
                return True
            return False

        if user.role == user.Role.IS_STUDENT and view.action == 'retrieve':
            return True

        return False


class FloorPermission(permissions.BasePermission):
    """
    - Superadmin: CRUD hammasini amalga oshiradi.
    - DormitoryAdmin: faqat o‘zining dormitory’siga floor yaratadi, tahrirlaydi, ko‘ra oladi.
    - Student: faqat floor'larni ko‘ra oladi.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.role == user.Role.IS_ADMIN:
            return True

        if user.role == user.Role.IS_STUDENT or user.role == user.Role.IS_SUPERADMIN:
            if view.action in ['list', 'retrieve']:
                return True
            return False

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Superadmin hammasini ko‘rishi mumkin
        if user.role == user.Role.IS_SUPERADMIN:
            return True

        # DormitoryAdmin faqat o‘zining dormitory’siga tegishli floor’ni tahrirlay oladi
        if user.role == user.Role.IS_ADMIN:
            if view.action in ['retrieve', 'update', 'destroy']:
                return obj.dormitory.admin == user
            return False

        # Student faqat floor’larni ko‘ra oladi, hech qanday o‘zgartirish kiritishga ruxsat yo‘q
        return view.action == 'retrieve'


class RoomPermission(permissions.BasePermission):
    """
    - Superadmin: CRUD hammasini amalga oshiradi.
    - DormitoryAdmin: faqat o‘zining dormitory’sidagi room’larni yaratadi, tahrirlaydi, ko‘ra oladi.
    - Student: faqat room'larni ko‘ra oladi.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        # Superadmin hammasini qila oladi
        if user.role == user.Role.IS_SUPERADMIN:
            return True

        # DormitoryAdmin faqat o‘zining dormitory’sidagi room’larni ko‘ra oladi
        if user.role == user.Role.IS_ADMIN:
            if view.action in ['list', 'retrieve', 'create', 'update']:
                return True
            return False

        # Student faqat ko‘ra oladi
        if user.role == user.Role.IS_STUDENT:
            if view.action in ['list', 'retrieve']:
                return True
            return False

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Superadmin hammasini ko‘rishi mumkin
        if user.role == user.Role.IS_SUPERADMIN:
            return True

        # DormitoryAdmin faqat o‘zining dormitory’siga tegishli room’ni tahrirlay oladi
        if user.role == user.Role.IS_ADMIN:
            if view.action == 'retrieve':
                return obj.dormitory.admin == user
            if view.action in ['update', 'destroy']:
                return obj.dormitory.admin == user
            return False

        # Student faqat room’larni ko‘ra oladi, hech qanday o‘zgartirish kiritishga ruxsat yo‘q
        return view.action == 'retrieve'

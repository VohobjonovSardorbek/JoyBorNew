from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class PaymentPermission(permissions.BasePermission):
    """
    To‘lovlarga oid permission:
    - Student o‘zining paymentlarini ko‘radi va tahrirlaydi.
    - SuperAdmin hammasini ko‘radi va tahrirlaydi.
    - Admin faqat ko‘rishi mumkin, o‘zgartira olmaydi.
    """

    def has_permission(self, request, view):
        # Barcha autentifikatsiya qilingan foydalanuvchilar ruxsatga ega
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # SuperAdmin barcha narsani ko‘ra va tahrir qila oladi
        if user.role == 'superadmin':
            return True

        # Admin faqat ko‘ra oladi (GET), lekin o‘zgartira olmaydi
        if user.role == 'admin':
            return request.method in permissions.SAFE_METHODS

        # Student faqat o‘ziga tegishli paymentlarni ko‘ra va tahrirlay oladi
        if user.role == 'atudent':
            return obj.student == user

        return False


class IsAdminOrDormitoryAdminOrReadOnly(permissions.BasePermission):
    """
    - SuperAdmin va DormitoryAdmin yaratishi va o‘zgartirishi mumkin.
    - Admin va Student faqat o‘qiy oladi (GET).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return (
                request.user.role == 'superadmin' or
                request.user.role == 'admin'
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
                request.user.role == 'superadmin' or
                request.user.role == 'admin'
        )


class IsAdminOrDormitoryAdminOrReadOnly(permissions.BasePermission):
    """
    Obuna yaratish va tahrirlash faqat admin va dormitory adminlariga ruxsat beriladi.
    Studentlarga esa faqat o'qish ruxsati.
    """

    def has_permission(self, request, view):
        # Faqat superadmin va dormitory adminlariga ruxsat
        if request.user.is_super_admin or request.user.is_dormitory_admin:
            return True
        # Faqat o'qish uchun ruxsat (Studentlarga)
        elif request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Admin va dormitory adminlari faqat o'z yaratgan obunalarini ko'ra oladi
        if request.user.is_super_admin:
            # Superadmin barcha obunalarni ko'ra oladi, faqat o'zi yaratganlarini tahrirlaydi
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return obj.created_by == request.user
            return True  # Superadmin barcha obunalarni ko'rishi mumkin

        elif request.user.is_dormitory_admin:
            # Dormitory admin faqat o'zi yaratgan obunalarni ko'ra oladi
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return obj.created_by == request.user
            return obj.dormitory.admin == request.user  # Faqat o'z yotoqxonasini ko'radi

        elif request.user.role == 'student':
            # Student faqat obuna ko'rish imkoniyatiga ega
            if request.method == 'GET':
                return True
            return False  # Tahrirlash va yaratishga ruxsat yo'q

        return False


class DormitorySubscriptionPermission(permissions.BasePermission):
    """
    Custom permission for DormitorySubscription:
    - Student: hech narsa qila olmaydi
    - DormitoryAdmin: faqat o'ziga tegishli subscription'ni ko‘ra oladi
    - Superadmin: hammasini ko‘radi, faqat o‘zi yaratganini tahrirlaydi
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        # Student hech narsa qila olmaydi
        if user.role == 'student':
            return False

        # Create/update faqat superadminlarga ruxsat
        if request.method not in SAFE_METHODS and user.role != 'superadmin':
            return False

        # Boshqa holatlarda (GET) superadmin va dormitoryadminlar ko‘ra oladi
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Student hech narsa qila olmaydi
        if user.role == 'student':
            return False

        # Superadmin hammasini ko‘radi, lekin tahrirlash faqat o‘zi yaratganiga
        if user.role == 'superadmin':
            if request.method in SAFE_METHODS:
                return True
            return obj.created_by == user

        # DormitoryAdmin: faqat ko‘rishi mumkin — agar dormitory unga tegishli bo‘lsa
        if user.role == 'admin' and request.method in SAFE_METHODS:
            return hasattr(user, 'dormitory') and obj.dormitory == user.dormitory

        return False

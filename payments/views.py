from django.contrib.auth.models import AnonymousUser
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied

from .models import PaymentByStudent, SubscriptionForStudent, SubscriptionPlanForDormitory, DormitorySubscription
from .permissions import PaymentPermission, IsAdminOrDormitoryAdminOrReadOnly, DormitorySubscriptionPermission
from .serializers import PaymentByStudentReadSerializer, PaymentByStudentWriteSerializer, \
    SubscriptionForStudentSerializer, SubscriptionPlanForDormitorySerializer, DormitorySubscriptionSerializer


class PaymentByStudentViewSet(viewsets.ModelViewSet):
    """
    Talabaning to‘lovlarini ko‘rish, qo‘shish va tahrirlash uchun ViewSet.
    """
    queryset = PaymentByStudent.objects.all().select_related('student')
    permission_classes = [PaymentPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['method', 'status']
    search_fields = ['student__username']
    ordering_fields = ['paid_at', 'amount']
    ordering = ['-paid_at']

    def get_queryset(self):
        """
        Foydalanuvchi o‘zining to‘lovlarini ko‘radi.
        Superuser barcha foydalanuvchilarning to‘lovlarini ko‘ra oladi.
        """
        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return PaymentByStudent.objects.none()
        role = getattr(user, 'role', None)

        if user.role == 'superadmin' or user.role == 'admin':
            return self.queryset
        elif user.role == 'student':
            return self.queryset.filter(student=user)
        return PaymentByStudent.objects.none()

    def get_serializer_class(self):
        """
        Harakat turiga qarab serializer tanlash:
        - list/retrieve => ReadSerializer
        - create/update => WriteSerializer
        """
        if self.action in ['list', 'retrieve']:
            return PaymentByStudentReadSerializer
        return PaymentByStudentWriteSerializer

    def perform_create(self, serializer):
        """
        To‘lovni yaratishda foydalanuvchini avtomatik bog‘lash.
        """
        serializer.save(student=self.request.user)

    @swagger_auto_schema(tags=['Studentning to\'lovlari'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Studentning to\'lovlari'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Studentning to\'lovlari'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Studentning to\'lovlari'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Studentning to\'lovlari'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Studentning to\'lovlari'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class SubscriptionForStudentViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionForStudent.objects.all().select_related('student__user__username', 'payment', 'dormitory')
    serializer_class = SubscriptionForStudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrDormitoryAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['dormitory', 'student', 'is_active', 'start_date', 'end_date']
    search_fields = ['student__user__username', 'dormitory__name']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return SubscriptionForStudent.objects.none()
        role = getattr(user, 'role', None)

        if user.role == 'superadmin':
            return self.queryset
        elif user.role == 'admin':
            return self.queryset.filter(dormitory__admin=user)
        elif user.role == 'student':
            return self.queryset.filter(student=user)
        return SubscriptionForStudent.objects.none()

    def perform_create(self, serializer):
        request = self.request
        user = request.user

        # Admin yoki yotoqxona admini bo‘lishi kerak
        if user.is_superuser or user.is_super_admin or user.is_dormitory_admin:
            serializer.save(created_by=user)  # created_by ni saqlaymiz
        else:
            raise PermissionDenied("Faqat admin yoki yotoqxona admini obuna yaratishi mumkin.")

    @swagger_auto_schema(tags=['Student uchun obuna'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student uchun obuna'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student uchun obuna'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student uchun obuna'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student uchun obuna'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student uchun obuna'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class SubscriptionPlanForDormitoryViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlanForDormitory.objects.all()
    serializer_class = SubscriptionPlanForDormitorySerializer
    permission_classes = [IsAdminOrDormitoryAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'duration_months', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'duration_months', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return SubscriptionPlanForDormitory.objects.none()
        role = getattr(user, 'role', None)

        if user.is_super_admin:
            # Superadmin barcha obunalarni ko'ra oladi
            return self.queryset
        elif user.is_dormitory_admin:
            # Dormitory admin faqat o'zining yotoqxonasidagi obunalarni ko'radi
            return self.queryset.filter(dormitory__admin=user)
        return SubscriptionPlanForDormitory.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_super_admin or user.is_dormitory_admin:
            serializer.save(created_by=user)
        else:
            raise PermissionDenied("Faqat admin yoki yotoqxona admini obuna yaratishi mumkin.")

    def perform_update(self, serializer):
        user = self.request.user
        if user.is_super_admin or user.is_dormitory_admin:
            if serializer.instance.created_by == user:
                serializer.save()
            else:
                raise PermissionDenied("Siz faqat o'zingiz yaratgan obunani tahrirlay olasiz.")
        else:
            raise PermissionDenied("Faqat super admin yoki yotoqxona admini obunani tahrirlay oladi.")

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_super_admin or user.is_dormitory_admin:
            if instance.created_by == user:
                instance.delete()
            else:
                raise PermissionDenied("Siz faqat o'zingiz yaratgan obunani o'chirishingiz mumkin.")
        else:
            raise PermissionDenied("Faqat admin yoki yotoqxona admini obunani o'chirishi mumkin.")

    @swagger_auto_schema(tags=['Yotoqxona obunasi uchun reja'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxona obunasi uchun reja'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxona obunasi uchun reja'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxona obunasi uchun reja'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxona obunasi uchun reja'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxona obunasi uchun reja'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class DormitorySubscriptionViewSet(viewsets.ModelViewSet):
    queryset = DormitorySubscription.objects.all()
    serializer_class = DormitorySubscriptionSerializer
    permission_classes = [DormitorySubscriptionPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['start_date', 'end_date']
    search_fields = ['dormitory__name', 'plan__name']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return DormitorySubscription.objects.none()
        role = getattr(user, 'role', None)

        if user.role == 'superadmin':
            return DormitorySubscription.objects.all()

        elif user.role == 'admin':
            # Faqat o'z dormitorysiga tegishli subscription
            return DormitorySubscription.objects.filter(dormitory__admin=user)

        return DormitorySubscription.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(tags=['Yotoqxonaning obunasi'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxonaning obunasi'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxonaning obunasi'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxonaning obunasi'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxonaning obunasi'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxonaning obunasi'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

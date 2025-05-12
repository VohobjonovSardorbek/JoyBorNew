from django.contrib.auth.models import AnonymousUser
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, filters
from rest_framework.permissions import IsAuthenticated

from .models import Student, Application
from .serializers import StudentSerializer, ApplicationSerializer
from .permissions import IsStudentOrAdminForOwnDormitory, IsAdminForDormitory, IsSuperAdminOrOwner
from django_filters.rest_framework import DjangoFilterBackend


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'university', 'faculty').all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['university', 'faculty', 'social_status']
    search_fields = ['passport_number', 'father_name', 'user__full_name']
    ordering_fields = ['created_at', 'discount']
    ordering = ['-created_at']

    def get_serializer_context(self):
        """
        Pass 'university_id' to serializer context for dynamic faculty queryset.
        """
        context = super().get_serializer_context()
        university_id = self.request.query_params.get('university_id')
        if university_id:
            context['university_id'] = university_id
        return context

    def get_queryset(self):
        """
        Optionally override to filter students by user or role.
        """
        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return Student.objects.none()
        role = getattr(user, 'role', None)

        if user.is_super_admin or user.is_staff:
            return self.queryset
        return self.queryset.filter(user=user)

    @swagger_auto_schema(tags=['Student'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Student'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filtirlash, izlash, tartiblash maydonlari
    filterset_fields = ['status', 'dormitory']
    search_fields = ['comment', 'dormitory__name']
    ordering_fields = ['submitted_at', 'reviewed_at']
    ordering = ['-submitted_at']

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return Application.objects.none()
        role = getattr(user, 'role', None)

        # Superadmin hamma arizalarni ko‘ra oladi
        if user.is_super_admin:
            return self.queryset

        # Admin faqat o‘zining yotoqxonasidagi arizalarni ko‘radi
        if user.is_dormitory_admin:
            return self.queryset.filter(dormitory__admin=user)

        # Student faqat o‘zining arizasini ko‘radi
        return self.queryset.filter(student=user)

    def perform_create(self, serializer):
        # Foydalanuvchini avtomatik bog‘lash
        serializer.save(student=self.request.user)

    def get_permissions(self):
        # Ariza yangilanishi uchun ruxsat
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsSuperAdminOrOwner]
        else:
            # Ariza ko‘rish uchun ruxsat
            self.permission_classes = [IsStudentOrAdminForOwnDormitory]
        return super().get_permissions()

    @swagger_auto_schema(tags=['Ariza'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Ariza'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Ariza'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Ariza'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Ariza'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Ariza'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
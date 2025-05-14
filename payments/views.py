from django.contrib.auth.models import AnonymousUser
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied

from .models import PaymentForStudent
from .permissions import PaymentPermission
from .serializers import PaymentForStudentReadSerializer, PaymentForStudentWriteSerializer


class PaymentForStudentViewSet(viewsets.ModelViewSet):
    queryset = PaymentForStudent.objects.all()
    permission_classes = [PaymentPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['method']
    search_fields = ['student__name']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):

        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return PaymentForStudent.objects.none()
        role = getattr(user, 'role', None)

        if user.role == 'superadmin' or user.role == 'admin':
            return self.queryset
        return PaymentForStudent.objects.none()

    def get_serializer_class(self):

        if self.action in ['list', 'retrieve']:
            return PaymentForStudentReadSerializer
        return PaymentForStudentWriteSerializer

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

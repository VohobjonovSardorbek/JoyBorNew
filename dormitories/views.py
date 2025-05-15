from sys import exception

from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Dormitory, Floor, Room
from .permissions import DormitoryPermission, FloorPermission, RoomPermission
from .serializers import DormitoryCreateUpdateSerializer, DormitorySerializer, FloorCreateUpdateSerializer, \
    FloorSerializer, RoomCreateUpdateSerializer, RoomSerializer


class DormitoryViewSet(viewsets.ModelViewSet):
    queryset = Dormitory.objects.all().select_related('university', 'admin')
    permission_classes = [DormitoryPermission]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DormitoryCreateUpdateSerializer
        return DormitorySerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return Dormitory.objects.none()
        role = getattr(user, 'role', None)

        if user.role == user.Role.IS_SUPERADMIN or user.role == user.Role.IS_STUDENT:
            return Dormitory.objects.all()

        elif user.role == user.Role.IS_ADMIN:
            return Dormitory.objects.filter(admin=user)

        return Dormitory.objects.none()

    @swagger_auto_schema(tags=['Yotoqxona'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxona'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxona'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxona'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == user.Role.IS_STUDENT or user.role == user.Role.IS_SUPERADMIN:
            raise PermissionDenied("Faqat admin  yotoqxona yarata oladi.")
        serializer.save(admin=user)

    def perform_update(self, serializer):
        user = self.request.user
        if user.role != user.Role.IS_ADMIN or serializer.instance.dormitory.admin != user:
            raise PermissionDenied("Faqat admin tahrirlashi mumkin.")
        serializer.save()

    @swagger_auto_schema(tags=['Yotoqxona'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Yotoqxona'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role != user.Role.IS_ADMIN and instance.dormitory.admin == user:
            raise PermissionDenied("Faqat dormitory admin o'z yotoqxonasida qavat o‘chira oladi.")
        instance.delete()


class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.select_related('dormitory').all()
    permission_classes = [IsAuthenticated, FloorPermission]

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return FloorCreateUpdateSerializer
        return FloorSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return Floor.objects.none()
        role = getattr(user, 'role', None)

        if user.role == user.Role.IS_SUPERADMIN:
            return Floor.objects.all()

        elif user.role == user.Role.IS_ADMIN:
            return Floor.objects.filter(dormitory__admin=user)

        return Floor.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != user.Role.IS_ADMIN:
            raise PermissionDenied("Faqat dormitory admin floor yaratishi mumkin.")

        try:
            dormitory = Dormitory.objects.get(admin=user)
        except Dormitory.DoesNotExist:
            raise ValidationError("Sizga hech qanday dormitory biriktirilmagan.")

        serializer.save(dormitory=dormitory)

    def perform_update(self, serializer):
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("Siz hali tizimga kirmadingiz.")

        if user.role != user.Role.IS_ADMIN:
            raise PermissionDenied("Faqat dormitory admin floor yangilashi mumkin.")

        try:
            dormitory = Dormitory.objects.get(admin=user)
        except Dormitory.DoesNotExist:
            raise ValidationError("Sizga hech qanday dormitory biriktirilmagan.")

        if serializer.instance.dormitory != dormitory:
            raise PermissionDenied("Faqat o‘z dormitory’ingizdagi floor’ni tahrirlay olasiz.")

        serializer.save(dormitory=dormitory)

    def destroy(self, request, *args, **kwargs):
        user = request.user

        if user.role != user.Role.IS_ADMIN:
            raise PermissionDenied("Faqat dormitory admin floor o‘chira oladi.")

        # O‘chirilayotgan obyektni olamiz
        instance = self.get_object()

        # Foydalanuvchiga tegishli dormitoryni olamiz
        try:
            dormitory = Dormitory.objects.get(admin=user)
        except Dormitory.DoesNotExist:
            raise PermissionDenied("Sizga hech qanday dormitory biriktirilmagan.")

        # O‘chirishga ruxsat bor-yo‘qligini tekshiramiz
        if instance.dormitory != dormitory:
            raise PermissionDenied("Siz faqat o‘z dormitory’ingizdagi floor’ni o‘chira olasiz.")

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(tags=['Qavat'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Qavat'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Qavat'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Qavat'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Qavat'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Qavat'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related('dormitory', 'floor').all()
    permission_classes = [RoomPermission]

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return RoomCreateUpdateSerializer
        return RoomSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            # Agar foydalanuvchi tizimga kirgan bo'lmasa, queryset bo'sh bo'ladi
            return Room.objects.none()

        role = getattr(user, 'role', None)

        if user.role == user.Role.IS_SUPERADMIN:
            return Room.objects.all()

        elif user.role == user.Role.IS_ADMIN:
            return Room.objects.filter(dormitory__admin=user)

        return Room.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_authenticated:
            raise PermissionDenied("Siz hali tizimga kirmadingiz.")

        if user.role != user.Role.IS_ADMIN:
            raise PermissionDenied("Faqat dormitory admin room yaratishi mumkin.")

        # Foydalanuvchiga biriktirilgan dormitoryni olish
        try:
            dormitory = Dormitory.objects.get(admin=user)
        except Dormitory.DoesNotExist:
            raise PermissionDenied("Sizga hech qanday dormitory biriktirilmagan.")

        # Floorni serializerdan olish
        floor = serializer.validated_data.get('floor')

        # Floor mavjudligini va aynan shu foydalanuvchining dormitorysiga tegishli ekanligini tekshirish
        if not floor:
            raise PermissionDenied("Floor ko‘rsatilmagan.")

        if floor.dormitory != dormitory:
            raise PermissionDenied("Siz faqat o‘z dormitory’ingizga tegishli floor ichida room yaratishingiz mumkin.")

        serializer.save(dormitory=dormitory)

    def perform_update(self, serializer):
        user = self.request.user

        if user.role != user.Role.IS_ADMIN:
            raise PermissionDenied("Faqat dormitory admin room’ni tahrirlay oladi.")

        try:
            dormitory = Dormitory.objects.get(admin=user)
        except Dormitory.DoesNotExist:
            raise PermissionDenied("Sizga hech qanday dormitory biriktirilmagan.")

        floor = serializer.validated_data.get('floor', serializer.instance.floor)

        if floor.dormitory != dormitory:
            raise PermissionDenied("Siz faqat o‘z dormitory’ingizdagi room’ni tahrirlay olasiz.")

        serializer.save(dormitory=dormitory)

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role != user.Role.IS_ADMIN:
            raise PermissionDenied("Faqat dormitory admin room’ni o‘chira oladi.")

        try:
            dormitory = Dormitory.objects.get(admin=user)
        except Dormitory.DoesNotExist:
            raise PermissionDenied("Sizga hech qanday dormitory biriktirilmagan.")

        if instance.floor.dormitory != dormitory:
            raise PermissionDenied("Siz faqat o‘z dormitory’ingizdagi room’ni o‘chira olasiz.")

        instance.delete()

    @swagger_auto_schema(tags=['Xona'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Xona'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Xona'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Xona'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Xona'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Xona'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
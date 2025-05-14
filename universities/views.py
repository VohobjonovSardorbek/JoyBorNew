from drf_yasg.utils import swagger_auto_schema

from accounts.permissions import IsAuthenticatedOrSuperAdminOnly, IsSuperAdmin
from dormitories.models import Floor
from .serializers import UniversitySerializer, FacultySerializer
from rest_framework import status
from rest_framework.response import Response
from universities.models import University, Faculty
from rest_framework import viewsets


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all().order_by('name')
    serializer_class = UniversitySerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return University.objects.none()
        return University.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.save()

    @swagger_auto_schema(tags=['Universitet'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Universitet'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Universitet'])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Universitet'])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Universitet'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Universitet'])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all().order_by('name')
    serializer_class = FacultySerializer
    permission_classes = [IsSuperAdmin]

    def perform_create(self, serializer):
        """
        Fakultet yaratishda kim tomonidan yaratildi (request.user).
        """
        instance = serializer.save()

    def perform_update(self, serializer):
        """
        Fakultet yangilanishida kim tomonidan yangilandi (request.user).
        """
        instance = serializer.save()

    def perform_destroy(self, instance):
        """
        Fakultet o'chirishda kim tomonidan o'chirildi (request.user).
        """
        instance.delete()

    def get_queryset(self):

        queryset = super().get_queryset()

        if getattr(self, 'swagger_fake_view', False):
            return Faculty.objects.none()

        university = self.request.query_params.get('university')
        if university:
            queryset = queryset.filter(university__id=university)
        return queryset

    @swagger_auto_schema(tags=['Fakultet'])
    def create(self, request, *args, **kwargs):
        """
        Fakultet yaratishdan oldin, universitet ID tekshiruvi.
        """
        university_id = request.data.get('university')
        if not university_id:
            return Response({"detail": "Universitet IDsi kerak."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Fakultet'])
    def update(self, request, *args, **kwargs):
        """
        Fakultetni yangilashda qo'shimcha tekshiruvlar.
        """
        instance = self.get_object()
        new_name = request.data.get('name')

        if instance.name != new_name:
            if Faculty.objects.filter(university=instance.university, name__iexact=new_name).exists():
                return Response({"detail": "Bunday nomli fakultet mavjud."}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Fakultet'])
    def destroy(self, request, *args, **kwargs):
        """
        Fakultetni o'chirishdan oldin log.
        """
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Fakultet'])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Fakultet'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Fakultet'])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

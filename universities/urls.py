from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UniversityViewSet, FacultyViewSet

router = DefaultRouter()

router.register('university', UniversityViewSet)
router.register('faculty', FacultyViewSet)

urlpatterns = [
    path('', include(router.urls))
]
from django.urls import path, include
from .views import StudentViewSet, ApplicationViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('student', StudentViewSet)
router.register('application', ApplicationViewSet)

urlpatterns = [
    path('', include(router.urls))
]
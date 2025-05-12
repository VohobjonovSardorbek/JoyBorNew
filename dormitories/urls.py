from django.urls import path, include

from .views import FloorViewSet, RoomViewSet, DormitoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('dormitory', DormitoryViewSet)
router.register('floor', FloorViewSet)
router.register('room', RoomViewSet)

urlpatterns = [
    path('', include(router.urls))
]
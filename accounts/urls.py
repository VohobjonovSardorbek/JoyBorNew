from django.urls import path, include
from .views import UserViewSet, UserProfileViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('user', UserViewSet)
router.register('userprofile', UserProfileViewSet)

urlpatterns = [
    path('', include(router.urls))
]
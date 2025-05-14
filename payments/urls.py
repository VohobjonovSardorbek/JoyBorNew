from django.urls import path, include

from .views import PaymentForStudentViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('payment_by_student', PaymentForStudentViewSet)
urlpatterns = [
    path('', include(router.urls))
]
from django.urls import path, include

from .models import SubscriptionPlanForDormitory
from .serializers import SubscriptionPlanForDormitorySerializer
from .views import SubscriptionForStudentViewSet, PaymentByStudentViewSet, DormitorySubscriptionViewSet, \
    SubscriptionPlanForDormitoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('payment_by_student', PaymentByStudentViewSet)
router.register('subscription_for_student', SubscriptionForStudentViewSet)
router.register('subscription_plan_for_dormitory', SubscriptionPlanForDormitoryViewSet)
router.register('dormitory_subscription', DormitorySubscriptionViewSet)

urlpatterns = [
    path('', include(router.urls))
]
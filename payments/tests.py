from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User
from dormitories.models import Dormitory
from students.models import Student
from payments.models import (
    PaymentByStudent,
    PaymentMethod,
    PaymentStatus,
    SubscriptionForStudent,
    SubscriptionPlanForDormitory,
    DormitorySubscription
)
from universities.models import University


class PaymentModelsTestCase(TestCase):
    def setUp(self):
        self.superadmin = User.objects.create_user(
            username='superadmin',
            email='superadmin@example.com',
            password='superpass',
            role=User.Role.IS_SUPERADMIN
        )

        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='studentpass',
            role=User.Role.IS_STUDENT
        )

        self.university = University.objects.create(name='Test University')

        self.dormitory = Dormitory.objects.create(
            name='Dorm A',
            university=self.university,
            address='Test Street',
            city='Test City',
            number_of_floors=3,
            subscription_end_date=timezone.now().date() + timedelta(days=30),
            admin=self.superadmin
        )

        self.student = Student.objects.create(
            user=self.student_user,
        )
        print(f"Student user: {self.student_user.username}")  # 👈 bu "student1" chiqishi kerak

    def test_payment_by_student_creation(self):
        payment = PaymentByStudent.objects.create(
            student=self.student_user,
            amount=Decimal('150000.00'),
            method=PaymentMethod.CASH,
            status=PaymentStatus.PENDING
        )
        self.assertEqual(str(payment), f"{self.student_user.username} - {payment.amount} so'm")
        self.assertEqual(payment.status, PaymentStatus.PENDING)

    def test_subscription_for_student(self):
        payment = PaymentByStudent.objects.create(
            student=self.student_user,
            amount=Decimal('100000.00'),
            method=PaymentMethod.CARD,
            status=PaymentStatus.SUCCESS
        )
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)

        sub = SubscriptionForStudent.objects.create(
            payment=payment,
            student=self.student,
            dormitory=self.dormitory,
            start_date=start_date,
            end_date=end_date,
            created_by=self.superadmin
        )

        self.assertEqual(str(sub), f"{self.student_user.username} - {self.dormitory} obunasi")
        self.assertFalse(sub.is_expired)

    def test_subscription_expired_property(self):
        sub = SubscriptionForStudent.objects.create(
            payment=None,
            student=self.student,
            dormitory=self.dormitory,
            start_date=timezone.now().date() - timedelta(days=40),
            end_date=timezone.now().date() - timedelta(days=1),
            created_by=self.superadmin
        )
        self.assertTrue(sub.is_expired)

    def test_subscription_plan_for_dormitory(self):
        plan = SubscriptionPlanForDormitory.objects.create(
            name='Premium Plan',
            description='Full access',
            price=Decimal('999999.99'),
            duration_months=6,
            is_active=True,
            created_by=self.superadmin
        )
        self.assertEqual(str(plan), f"{plan.name} - {plan.price} so'm / {plan.duration_months} oy (Faol)")

    def test_dormitory_subscription_save_logic(self):
        plan = SubscriptionPlanForDormitory.objects.create(
            name='6 oyli',
            price=Decimal('500000.00'),
            duration_months=6,
            created_by=self.superadmin
        )

        sub = DormitorySubscription.objects.create(
            dormitory=self.dormitory,
            plan=plan,
            created_by=self.superadmin
        )

        expected_end_date = sub.start_date + timedelta(days=30 * plan.duration_months)
        self.assertEqual(sub.end_date.month, (sub.start_date + timedelta(days=30 * 6)).month)
        self.assertEqual(str(sub), f"{self.dormitory.name} → {plan.name}")

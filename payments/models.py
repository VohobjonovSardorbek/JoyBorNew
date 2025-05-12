from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone
from accounts.models import User
from dormitories.models import Dormitory
from students.models import Student


class PaymentMethod(models.TextChoices):
    CLICK = 'click', 'Click'
    PAYME = 'payme', 'PayMe'
    CASH = 'cash', 'Naqd'
    CARD = 'card', 'Karta orqali'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Kutilmoqda'
    SUCCESS = 'success', 'To‘landi'
    FAILED = 'failed', 'Muvaffaqiyatsiz'


class PaymentByStudent(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments', limit_choices_to={'role': User.Role.IS_STUDENT})
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    paid_at = models.DateTimeField(default=timezone.now)
    receipt = models.FileField(upload_to='payment_receipts/', blank=True, null=True)  # 📎 To‘lov chek/fayli

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f"{self.student.username} - {self.amount} so'm"


class SubscriptionForStudent(models.Model):
    payment = models.OneToOneField(PaymentByStudent, on_delete=models.SET_NULL, null=True,
                                   related_name='pay_by_student')
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='subscription')
    dormitory = models.ForeignKey(Dormitory, on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='created_by', null=True, limit_choices_to={'role__in': [User.Role.IS_ADMIN, User.Role.IS_SUPERADMIN]})

    def __str__(self):
        return f"{self.student.user.username} - {self.dormitory} obunasi"

    @property
    def is_expired(self):
        from datetime import date
        return date.today() > self.end_date


class SubscriptionPlanForDormitory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.PositiveIntegerField(default=12)
    is_active = models.BooleanField(default=True)
    payment_proof = models.FileField(
        upload_to='payment_proofs/',
        blank=True,
        null=True,
        help_text="To‘lovni tasdiqlovchi hujjat (rasm yoki PDF)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=False, default=1, limit_choices_to={'role__in': [User.Role.IS_ADMIN, User.Role.IS_SUPERADMIN]})

    def __str__(self):
        return f"{self.name} - {self.price} so'm / {self.duration_months} oy ({'Faol' if self.is_active else 'Faolsiz'})"


class DormitorySubscription(models.Model):
    dormitory = models.OneToOneField(Dormitory, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlanForDormitory, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=False, default=1, limit_choices_to={'role__in': [User.Role.IS_ADMIN, User.Role.IS_SUPERADMIN]})
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan:
            self.end_date = self.start_date + relativedelta(months=self.plan.duration_months)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.dormitory.name} → {self.plan.name}"

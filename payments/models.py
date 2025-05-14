from django.db import models
from django.utils import timezone
from students.models import Student


class Month(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Naqd'
    CARD = 'card', 'Karta orqali'


class PaymentForStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='Talaba')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    month = models.ManyToManyField(Month)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.amount} so'm"

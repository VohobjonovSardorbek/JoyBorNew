from django.db import models
from django.utils import timezone
from accounts.models import User
from dormitories.models import Dormitory
from universities.models import University, Faculty


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.IS_STUDENT})
    passport_number = models.CharField(max_length=9, unique=True)
    father_name = models.CharField(max_length=100)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    additional_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    discount = models.CharField(max_length=255, blank=True, null=True)
    social_status = models.CharField(max_length=255, blank=True, null=True)
    payment_proof = models.FileField(
        upload_to='payment_proofs/',
        blank=True,
        null=True,
        help_text="To‘lovni tasdiqlovchi hujjat (rasm yoki PDF)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()}"


APPLICATION_STATUS = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]


class Application(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.IS_STUDENT})
    dormitory = models.ForeignKey(Dormitory, on_delete=models.CASCADE)
    student_document = models.FileField(upload_to='student_ID/', blank=True, null=True,
                                        verbose_name="Student's document")
    status = models.CharField(max_length=10, choices=APPLICATION_STATUS, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Application by {self.student.get_full_name()} to {self.dormitory.name}"

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address must be provided')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        IS_STUDENT = 'student', 'Student'
        IS_ADMIN = 'admin', 'Admin'
        IS_SUPERADMIN = 'superadmin', 'Super Admin'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.IS_STUDENT)
    status = models.CharField(max_length=20,
                              choices=[('active', 'Active'), ('inactive', 'Inactive'), ('blocked', 'Blocked')],
                              default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reset_password_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password_token_expires = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    @property
    def is_super_admin(self):
        return self.role == self.Role.IS_SUPERADMIN

    @property
    def is_dormitory_admin(self):
        return self.role == self.Role.IS_ADMIN

    @property
    def is_student(self):
        return self.role == self.Role.IS_STUDENT


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\+998\d{9}$')],
        verbose_name=_('Phone number')
    )
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    @property
    def user_status(self):
        return self.user.status

    class Meta:
        ordering = ['-created_at']

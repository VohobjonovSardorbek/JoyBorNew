from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from universities.models import University

User = get_user_model()


class Dormitory(models.Model):
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('pending', _('Pending')),
        ('inactive', _('Inactive'))
    )

    name = models.CharField(max_length=255)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)
    address = models.TextField()
    number_of_floors = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    admin = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='director_dormitories',
                                 verbose_name=_('Admin'))
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='active', verbose_name=_('Status'))
    contact_info = models.TextField(blank=True, null=True, verbose_name=_('Contact information'))
    latitude = models.FloatField(blank=True, null=True, verbose_name=_('Latitude'))
    longitude = models.FloatField(blank=True, null=True, verbose_name=_('Longitude'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}) - {self.university.name if self.university else 'No University'}"

    class Meta:
        verbose_name = _('Dormitory')
        verbose_name_plural = _('Dormitories')
        ordering = ['name']


class Floor(models.Model):
    GENDER_CHOICES = (
        ('male', _('Male')),
        ('female', _('Female')),
    )

    name = models.CharField(max_length=100)
    dormitory = models.ForeignKey(Dormitory, on_delete=models.CASCADE, related_name='floors')
    gender_type = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default='female',
        verbose_name=_('Gender type')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Floor {self.name} - {self.dormitory.name}"

    class Meta:
        verbose_name = _('Floor')
        verbose_name_plural = _('Floors')
        ordering = ['dormitory', 'name']
        unique_together = ('dormitory', 'name')


class Room(models.Model):
    dormitory = models.ForeignKey(Dormitory, on_delete=models.CASCADE, related_name='dormitories', blank=True,
                                  null=True)
    floor = models.ForeignKey(Floor, related_name='floors', on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    current_occupancy = models.PositiveSmallIntegerField(default=0)

    @property
    def is_full(self):
        return self.current_occupancy >= self.capacity

    class Meta:
        unique_together = ('floor', 'room_number')
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        ordering = ['floor', 'room_number']

    def __str__(self):
        return f"Floor {self.floor.floor_number} - Room {self.room_number}"


class DormitoryImage(models.Model):
    dormitory = models.ForeignKey(Dormitory, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='dormitories/')

    def __str__(self):
        return f"{self.dormitory.name} Image"

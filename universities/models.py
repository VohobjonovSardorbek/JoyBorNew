from django.db import models
from django.utils.translation import gettext_lazy as _


class University(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    contact_info = models.TextField(blank=True, null=True, verbose_name=_('Contact information'))
    website = models.URLField(blank=True, null=True, verbose_name=_('Website'))
    logo = models.ImageField(upload_to='university_logos/', blank=True, null=True, verbose_name=_('Logo'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('University')
        verbose_name_plural = _('Universities')
        ordering = ['name']


class Faculty(models.Model):
    university = models.ForeignKey(University, related_name='faculties', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_('Faculty name'))

    class Meta:
        verbose_name = _('Faculty')
        verbose_name_plural = _('Faculties')
        unique_together = ('university', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.university.name} - {self.name}"

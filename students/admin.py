from django.contrib import admin
from .models import Student, Application
from django.utils import timezone


class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'passport_number', 'middle_name', 'faculty', 'created_at')
    list_filter = ('faculty', 'created_at')
    search_fields = ('name', 'passport_number', 'middle_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Agar talaba mavjud bo'lsa
            fieldsets += (
                ('Additional Info', {
                    'fields': ('additional_phone', 'emergency_contact_name', 'emergency_contact_phone', 'discount',
                               'social_status', 'payment_proof')
                }),
            )
        return fieldsets


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'dormitory', 'submitted_at', 'comment')
    list_filter = ('dormitory', 'submitted_at')
    search_fields = ('student__name', 'dormitory__name')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at',)



admin.site.register(Student, StudentAdmin)
admin.site.register(Application, ApplicationAdmin)

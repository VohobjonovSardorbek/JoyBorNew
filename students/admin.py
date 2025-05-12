from django.contrib import admin
from .models import Student, Application
from django.utils import timezone


class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'passport_number', 'father_name', 'university', 'faculty', 'created_at')
    list_filter = ('university', 'faculty', 'created_at')
    search_fields = ('user__full_name', 'passport_number', 'father_name', 'emergency_contact_name')
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
    list_display = ('student', 'dormitory', 'status', 'submitted_at', 'reviewed_at', 'comment')
    list_filter = ('status', 'dormitory', 'submitted_at')
    search_fields = ('student__full_name', 'dormitory__name')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at', 'reviewed_at')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Agar ariza mavjud bo'lsa
            fieldsets += (
                ('Review Details', {
                    'fields': ('status', 'reviewed_at', 'comment')
                }),
            )
        return fieldsets

    def save_model(self, request, obj, form, change):
        if obj.status == 'approved' and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)


admin.site.register(Student, StudentAdmin)
admin.site.register(Application, ApplicationAdmin)

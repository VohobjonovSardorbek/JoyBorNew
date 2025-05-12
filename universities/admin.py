from django.contrib import admin
from .models import University, Faculty


class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'created_at', 'updated_at')
    list_filter = ('city', 'created_at')
    search_fields = ('name', 'city', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'city', 'address', 'description', 'contact_info', 'website', 'logo')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


class FacultyAdmin(admin.ModelAdmin):
    list_display = ('university', 'name')
    list_filter = ('university',)
    search_fields = ('name', 'university__name')
    ordering = ('university__name', 'name')

    fieldsets = (
        (None, {
            'fields': ('university', 'name')
        }),
    )


admin.site.register(University, UniversityAdmin)
admin.site.register(Faculty, FacultyAdmin)

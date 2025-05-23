from django.contrib import admin
from .models import Dormitory, Floor, Room, DormitoryImage


class DormitoryAdmin(admin.ModelAdmin):
    list_display = (
    'name', 'university', 'status', 'admin', 'created_at', 'updated_at')
    list_filter = ('status', 'university', 'admin')
    search_fields = ('name', 'university__name')
    ordering = ('-created_at',)
    fields = (
    'name', 'university', 'address', 'number_of_floors', 'description', 'admin',
    'status', 'contact_info', 'latitude', 'longitude', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Agar dormitory mavjud bo'lsa
            fieldsets += (
                ('Location', {
                    'fields': ('latitude', 'longitude')
                }),
            )
        return fieldsets


class FloorAdmin(admin.ModelAdmin):
    list_display = ('name', 'dormitory', 'gender_type', 'created_at')
    list_filter = ('gender_type', 'dormitory')
    search_fields = ('dormitory__name', 'name')
    ordering = ('dormitory',)


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'dormitory', 'floor', 'capacity', 'current_occupancy', 'created_at')
    list_filter = ('floor',)
    search_fields = ('room_number', 'dormitory__name')
    ordering = ('floor', 'room_number')

    def save_model(self, request, obj, form, change):
        if obj.current_occupancy > obj.capacity:
            raise ValueError("Current occupancy cannot exceed room capacity.")
        super().save_model(request, obj, form, change)


class DormitoryImageAdmin(admin.ModelAdmin):
    list_display = ('dormitory', 'image')
    search_fields = ('dormitory__name',)


admin.site.register(Dormitory, DormitoryAdmin)
admin.site.register(Floor, FloorAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(DormitoryImage, DormitoryImageAdmin)

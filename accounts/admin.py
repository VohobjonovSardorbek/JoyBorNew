from django.contrib import admin
from .models import User, UserProfile


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'email', 'role', 'status', 'created_at', 'updated_at')
    list_filter = ('role', 'status', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)
    fields = ('username','password', 'email', 'role', 'status', 'is_staff', 'is_superuser', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Agar foydalanuvchi mavjud bo'lsa
            fieldsets += (
                ('Password reset', {
                    'fields': ('reset_password_token', 'reset_password_token_expires')
                }),
            )
        return fieldsets


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'profile_picture', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user')  # Boshqa so'rovlar bilan birga user ma'lumotlarini olish


admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'status', 'is_staff', 'is_superuser', 'created_at')
    list_filter = ('role', 'status', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ()}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
        (_('Extra info'), {'fields': ('role', 'status', 'reset_password_token', 'reset_password_token_expires')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'status'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'profile_picture', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')

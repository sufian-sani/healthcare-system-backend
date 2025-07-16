from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id', 'full_name', 'mobile_number', 'role', 'is_staff', 'created_at')
    search_fields = ('full_name', 'mobile_number')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('mobile_number', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'role', 'address', 'profile_image')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'mobile_number', 'password1', 'password2', 'role')}
        ),
    )

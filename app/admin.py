from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ('email', 'username', 'platform', 'insta_handle', 'is_staff', 'is_active',)
    list_filter = ('email', 'username', 'platform', 'insta_handle', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'platform', 'insta_handle', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'platform', 'insta_handle', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'username')
    ordering = ('email', 'username')

admin.site.register(User, CustomUserAdmin)
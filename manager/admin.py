from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Manager, Branch


class CustomUserAdmin(UserAdmin):
    model = Manager
    list_display = ('username', 'email', 'firstname', 'lastname', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('firstname', 'lastname')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    # Remove the default 'filter_horizontal' settings
    filter_horizontal = ()

# Register your models here.
admin.site.register(Manager, CustomUserAdmin)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


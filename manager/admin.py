from django.contrib import admin
from .models import Manager, Branch


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'firstname', 'lastname', 'is_active', 'is_staff')
    search_fields = ('email', 'username', 'firstname', 'lastname')
    list_filter = ('is_active', 'is_staff')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Register your models here.

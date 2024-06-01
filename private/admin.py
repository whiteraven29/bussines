from django.contrib import admin
from .models import Single

# Register your models here.
class SingleAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'username', 'email', 'password')  # Removed is_active and is_staff
    search_fields = ('email', 'username', 'firstname', 'lastname')
    list_filter = ()  # Removed is_active and is_staff

admin.site.register(Single, SingleAdmin)
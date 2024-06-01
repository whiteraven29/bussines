from django.contrib import admin
from .models import Worker, Item, ItemReport

# Register your models here.


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'branch')
    search_fields = ('first_name', 'last_name', 'branch__name')
    list_filter = ('branch',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'worker')
    search_fields = ('name', 'worker__first_name', 'worker__last_name')
    list_filter = ('worker__branch',)

@admin.register(ItemReport)
class ItemReportAdmin(admin.ModelAdmin):
    list_display = ('item', 'date')
    search_fields = ('item__name', 'date')
    list_filter = ('item__worker__branch',)

admin.site.register(Worker, WorkerAdmin)

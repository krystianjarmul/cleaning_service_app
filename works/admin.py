from django.contrib import admin

from . import models

@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'company_name', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'company_name')
    list_filter = ('created_at', 'updated_at')


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'hourly_rate', 'created_at', 'updated_at')
    search_fields = ('name', 'company_name')
    list_filter = ('created_at', 'updated_at')


@admin.register(models.Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('employee', 'customer', 'created_at', 'updated_at')
    search_fields = ('employee__name', 'customer__name')
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ('employee', 'customer')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'customer')

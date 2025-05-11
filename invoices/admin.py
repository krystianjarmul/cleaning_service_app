from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from . import models
from .forms import GenerateInvoiceForm
from .tasks import generate_customer_invoices


@admin.register(models.Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ['name', 'generate_invoices']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:employer_id>/generate-invoices/',
                self.admin_site.admin_view(self.generate_invoices_view),
                name='generate-invoices'
            ),
        ]
        return custom_urls + urls

    def generate_invoices_view(self, request, employer_id):
        if request.method == 'POST':
            form = GenerateInvoiceForm(request.POST)
            if form.is_valid():
                generate_customer_invoices.delay(
                    month=form.cleaned_data['month'],
                    last_invoice_number=form.cleaned_data['last_invoice_number'],
                )

                messages.success(request, 'Invoices has been created.')
                url = reverse('admin:invoices_employer_changelist')
                return redirect(url)

            else:
                messages.error(request, 'Creating invoice has failed')
        else:
            form = GenerateInvoiceForm()

        context = dict(
            self.admin_site.each_context(request),
            title='Generate Customer Invoices',
            form=form,
        )
        return TemplateResponse(request, "admin/generate_invoice.html", context)

    @staticmethod
    def generate_invoices(obj):
        url = reverse('admin:generate-invoices', args=[obj.id])
        return format_html(
            '<a target="_blank" href="{url}">Generate</a>',
            url=url
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'Price', 'id']
    search_fields = ['name']

    def Price(self, obj):
        return f'{obj.price / 100}'


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']


@admin.register(models.Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer__name', 'employee__name', 'hours', 'date']
    search_fields = ['customer__name', 'employee__name', 'date']
    autocomplete_fields = ['customer', 'employee']


@admin.register(models.CustomerInvoice)
class CustomerInvoiceAdmin(admin.ModelAdmin):
    list_display = ['number', 'customer__name', 'created_at']
    search_fields = ['customer__name', 'created_at']

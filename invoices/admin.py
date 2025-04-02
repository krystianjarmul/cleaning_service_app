from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from . import models
from .forms import GenerateInvoiceForm
from .models import Customer
from .services import create_customer_invoice


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    change_list_template = 'admin/customer/change_list.html'
    list_display = ['name', 'price', 'id', 'generate_invoice']
    search_fields = ['name']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:customer_id>/generate-invoice/',
                self.admin_site.admin_view(self.generate_invoice_view),
                name='generate-invoice'
            ),
            path(
                'generate-invoices/',
                self.admin_site.admin_view(self.generate_invoices_view),
                name='generate-invoices'
            ),
        ]
        return custom_urls + urls

    def generate_invoice_view(self, request, customer_id):
        if request.method == 'POST':
            form = GenerateInvoiceForm(request.POST)
            if form.is_valid():
                create_customer_invoice(
                    customer_id=customer_id,
                    start_date=form.cleaned_data['start_date'],
                    end_date=form.cleaned_data['end_date']
                )
                messages.success(request, 'Invoice has been created.')
                url = reverse('admin:invoices_customer_changelist')
                return redirect(url)

            else:
                messages.error(request, 'Creating invoice has failed')
        else:
            form = GenerateInvoiceForm()
        context = dict(
            self.admin_site.each_context(request),
            title='Generate Invoice View',
            form=form,
        )
        return TemplateResponse(request, "admin/generate_invoice.html", context)

    def generate_invoices_view(self, request):

        customer_ids = Customer.objects.values_list('id', flat=True)

        if request.method == 'POST':
            form = GenerateInvoiceForm(request.POST)
            if form.is_valid():
                for customer_id in customer_ids:
                    create_customer_invoice(
                        customer_id=customer_id,
                        start_date=form.cleaned_data['start_date'],
                        end_date=form.cleaned_data['end_date']
                    )
                messages.success(request, 'Invoices has been created.')
                url = reverse('admin:invoices_customer_changelist')
                return redirect(url)

            else:
                messages.error(request, 'Creating invoice has failed')
        else:
            form = GenerateInvoiceForm()
        context = dict(
            self.admin_site.each_context(request),
            title='Generate Invoice View',
            form=form,
        )
        return TemplateResponse(request, "admin/generate_invoice.html", context)


    def generate_invoice(self, obj):
        url = reverse('admin:generate-invoice', args=[obj.id])
        return format_html(
            '<a target="_blank" href="{url}">Generate Invoice</a>',
            url=url
        )


@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']


@admin.register(models.Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer__name', 'employee__name', 'hours', 'date']
    search_fields = ['customer__name', 'employee__name', 'date']


@admin.register(models.Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename','type', 'file_link', 'created_at']

    def file_link(self, obj):
        if obj.file:
            return format_html(f'<a href="{obj.file.url}" target="_blank">Download</a>')
        return "-"

    file_link.short_description = "Invoice File"


# TODO move to separate app (pycharm)
# TODO create custom admin view for adding working days
#  -> one employee and many customers and it generates many works
# TODO create custom admin view for generating invoices for customers
# TODO create custom admin view for generating invoices for employees

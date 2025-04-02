import datetime
from io import BytesIO

from django.core.files.base import ContentFile
from django.db.models import ExpressionWrapper, Value, F, IntegerField
from docxtpl import DocxTemplate

from .data.customers import CUSTOMERS
from .data.employees import EMPLOYEES
from .models import Employee, Customer, Work, Invoice

EMPLOYEE_INVOICE_TEMPLATE = 'invoices/templates/employee.docx'
CUSTOMER_INVOICE_TEMPLATE = 'invoices/templates/customer.docx'


def delete_customers_and_employees():
    Employee.objects.all().delete()
    Customer.objects.all().delete()

def init_customers_and_employees():

    employees = [
        Employee(
            name=employee['name'],
            data=employee['data'],
            is_employer=employee.get('is_employer', False)
        )
        for employee in EMPLOYEES
    ]
    customers = [
        Customer(
            name=customer['name'],
            price=customer['price'],
            data=customer['data']
        )
        for customer in CUSTOMERS
    ]

    Employee.objects.bulk_create(employees)
    Customer.objects.bulk_create(customers)


def add_working_day(employee_id: int, customer_ids: list[int], date: datetime.date):
    works = [
        Work(customer_id=customer_id, employee_id=employee_id, date=date)
        for customer_id in customer_ids
    ]
    Work.objects.bulk_create(works)


def create_customer_invoice(
    customer_id: int, 
    start_date: datetime.date,
    end_date: datetime.date,
):
    customer = Customer.objects.prefetch_related('works').filter(id=customer_id).first()
    employer = Employee.objects.filter(is_employer=True).first()

    works = (
        customer
        .works
        .filter(date__gte=start_date, date__lte=end_date)
        .annotate(
            total=ExpressionWrapper(
                Value(customer.price) * F('hours'),
                output_field=IntegerField()
            )
        )
    )
    total_price = 0
    for work in works:
        work.total = work.total / 100
        total_price += work.total

    today = datetime.datetime.now()

    context = {
        "c": customer,
        "e": employer,
        "total_price": total_price,
        "works": works,
        "issue_date": today.strftime("%d.%m.%Y"),
        "year": today.year,
        "invoice_number": 1
    }

    filename = (
        f"{customer.name.lower()}_{today.date()}.docx"
        .replace(' ', '_')
        .replace('-', '_')
    )

    generate_invoice(
        template=CUSTOMER_INVOICE_TEMPLATE,
        context=context,
        filename=filename
    )


def create_employee_invoice(
    employee_id: int, 
    start_date: datetime.date,
    end_date: datetime.date,
):
    employee = Employee.objects.prefetch_related('works').filter(id=employee_id).first()

    works = employee.works.filter(date__gte=start_date, date__lte=end_date)

    context = {
        "works": works
    }

    filename = (
        f"{employee.name.lower()}_{datetime.datetime.now()}.docx"
        .replace(' ', '_')
        .replace('-', '_')
    )

    generate_invoice(
        filename=filename,
        template=EMPLOYEE_INVOICE_TEMPLATE,
        context=context
    )


def generate_invoice(filename: str, template: str, context: dict):

    file_buffer = BytesIO()

    doc = DocxTemplate(template)
    doc.render(context)
    doc.save(file_buffer)

    file_buffer.seek(0)
    django_file = ContentFile(file_buffer.read(), name=filename)

    invoice = Invoice(filename=filename)
    invoice.file.save(filename, django_file)
    invoice.save()

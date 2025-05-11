import datetime

from django.db.models import (
    QuerySet, Prefetch, Sum, ExpressionWrapper, F, IntegerField
)

from invoices.models import Employer, Work, Customer, CustomerInvoice, Employee


class EmployerRepository:

    @staticmethod
    def get():
        return Employer.objects.first()

    @staticmethod
    def create(data: dict):
        return Employer.objects.create(**data)

    @staticmethod
    def delete_all():
        Employer.objects.all().delete()


class CustomerRepository:

    @staticmethod
    def get_for_invoice(
            start_date: datetime.date,
            end_date: datetime.date,
            works: QuerySet[Work]
    ):
        return (
            Customer.objects
            .filter(works__date__range=(start_date, end_date))
            .prefetch_related(
                Prefetch('works', queryset=works)
            )
            .distinct()
        )

    @staticmethod
    def create_many(data: list[dict]):
        customers = [Customer(**item) for item in data]
        Customer.objects.bulk_create(customers)

    @staticmethod
    def delete_all():
        Customer.objects.all().delete()


class EmployeeRepository:

    @staticmethod
    def create_many(data: list[dict]):
        employees = [Employee(**item) for item in data]
        Employee.objects.bulk_create(employees)

    @staticmethod
    def delete_all():
        Employee.objects.all().delete()


class WorkRepository:

    @staticmethod
    def get_for_invoice(
            start_date: datetime.date, end_date: datetime.date
    ) -> QuerySet[Work]:
        return (
            Work.objects
            .filter(date__range=(start_date, end_date))
            .select_related('customer')
            .annotate(
                total_price=Sum(
                    ExpressionWrapper(
                        F('customer__price') * F('hours'),
                        output_field=IntegerField()
                    )
                )
            )
            .order_by('date')
        )


class CustomerInvoiceRepository:

    @staticmethod
    def create_draft(customer_id: int, data: dict) -> CustomerInvoice:
        return CustomerInvoice(
            customer_id=customer_id,
            data=data,
        )

    @staticmethod
    def create_many(invoices: list[CustomerInvoice]):
        CustomerInvoice.objects.bulk_create(invoices)

    @staticmethod
    def update_many(invoices: list[CustomerInvoice]):
        CustomerInvoice.objects.bulk_update(
            invoices,
            fields=['data', 'updated_at']
        )

    @staticmethod
    def get_all() -> QuerySet[CustomerInvoice]:
        return CustomerInvoice.objects.all()

    @staticmethod
    def get_by_month(year: int, month: int) -> QuerySet[CustomerInvoice]:
        return CustomerInvoice.objects.filter(
            data__year=year,
            data__month=month
        )

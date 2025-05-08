from django.core.management.base import BaseCommand

from invoices.repositories import (
    EmployeeRepository,
    EmployerRepository,
    CustomerRepository
)
from invoices.services import CleanDatabaseService


class Command(BaseCommand):
    help = 'Clean all database rows.'

    def handle(self, *args, **options):
        customer_repo = CustomerRepository()
        employee_repo = EmployeeRepository()
        employer_repo = EmployerRepository()

        service = CleanDatabaseService(
            customer_repo=customer_repo,
            employee_repo=employee_repo,
            employer_repo=employer_repo
        )
        service.execute()

        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

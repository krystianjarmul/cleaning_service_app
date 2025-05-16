from django.core.management.base import BaseCommand

from invoices.repositories import (
    EmployeesRepository,
    EmployersRepository,
    CustomersRepository
)
from invoices.services import CleanDatabaseService


class Command(BaseCommand):
    help = 'Clean all database rows.'

    def handle(self, *args, **options):
        customer_repo = CustomersRepository()
        employee_repo = EmployeesRepository()
        employer_repo = EmployersRepository()

        service = CleanDatabaseService(
            customer_repo=customer_repo,
            employee_repo=employee_repo,
            employer_repo=employer_repo
        )
        service.execute()

        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

from django.core.management.base import BaseCommand

from invoices.drive import GoogleDriveClient
from invoices.repositories import (
    EmployeeRepository,
    EmployerRepository,
    CustomerRepository
)
from invoices.services import InitDatabaseService


class Command(BaseCommand):
    help = 'Initialise customers and employees data in database for invoices.'

    def handle(self, *args, **options):
        drive = GoogleDriveClient()

        customer_repo = CustomerRepository()
        employee_repo = EmployeeRepository()
        employer_repo = EmployerRepository()

        service = InitDatabaseService(
            drive=drive,
            customer_repo=customer_repo,
            employee_repo=employee_repo,
            employer_repo=employer_repo
        )
        service.execute()

        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

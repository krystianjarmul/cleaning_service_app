from django.core.management.base import BaseCommand

from invoices.drive import GoogleDriveClient
from invoices.repositories import (
    EmployeesRepository,
    EmployersRepository,
    CustomersRepository
)
from invoices.services import InitDatabaseService


class Command(BaseCommand):
    help = 'Initialise customers and employees data in database for invoices.'

    def handle(self, *args, **options):
        drive = GoogleDriveClient()

        customers_repo = CustomersRepository()
        employees_repo = EmployeesRepository()
        employers_repo = EmployersRepository()

        service = InitDatabaseService(
            drive=drive,
            customers_repo=customers_repo,
            employees_repo=employees_repo,
            employers_repo=employers_repo
        )
        service.execute()

        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

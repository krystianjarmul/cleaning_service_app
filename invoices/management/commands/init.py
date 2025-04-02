from django.core.management.base import BaseCommand

from invoices.services import (
    init_customers_and_employees,
    delete_customers_and_employees
)


class Command(BaseCommand):
    help = 'Initialise customers and employees data in database for invoices.'

    def handle(self, *args, **options):
        delete_customers_and_employees()
        init_customers_and_employees()
        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

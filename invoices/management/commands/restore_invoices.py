from django.core.management.base import BaseCommand

from invoices.tasks import restore_customer_invoices


class Command(BaseCommand):
    help = 'Restore invoices data from database to Google Drive.'

    def handle(self, *args, **options):
        restore_customer_invoices.delay()

        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

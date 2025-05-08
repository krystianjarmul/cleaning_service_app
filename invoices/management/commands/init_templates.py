from django.core.management.base import BaseCommand

from invoices.services import InitTemplateService
from invoices.drive import GoogleDriveClient


class Command(BaseCommand):
    help = 'Initialise customers and employees data in database for invoices.'

    def handle(self, *args, **options):
        drive = GoogleDriveClient()

        service = InitTemplateService(drive=drive)
        service.execute()

        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

from django.core.management.base import BaseCommand

from invoices.services import DownloadTemplateService
from invoices.drive import GoogleDriveClient


class Command(BaseCommand):
    help = 'Downloads invoice templates.'

    def handle(self, *args, **options):
        drive = GoogleDriveClient()

        service = DownloadTemplateService(drive=drive)
        service.execute()

        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

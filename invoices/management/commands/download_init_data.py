from django.core.management.base import BaseCommand

from invoices.services import DownloadInitDataService
from invoices.drive import GoogleDriveClient


class Command(BaseCommand):
    help = 'Downloads init data.'

    def handle(self, *args, **options):
        drive = GoogleDriveClient()

        service = DownloadInitDataService(drive=drive)
        service.execute()

        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

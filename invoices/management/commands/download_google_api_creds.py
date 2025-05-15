from django.core.management.base import BaseCommand

from invoices.services import DownloadGoogleAPICredsService
from invoices.drive import GoogleDriveClient


class Command(BaseCommand):
    help = 'Downloads Google API credentials json file.'

    def handle(self, *args, **options):
        drive = GoogleDriveClient()

        service = DownloadGoogleAPICredsService(drive=drive)
        service.execute()

        self.stdout.write(self.style.SUCCESS('Command executed successfully!'))

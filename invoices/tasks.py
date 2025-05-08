import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from invoices.repositories import (
    EmployerRepository, CustomerRepository, WorkRepository,
    CustomerInvoiceRepository
)
from invoices.services import GenerateCustomerInvoicesService, \
    RestoreCustomerInvoicesService
from invoices.drive import GoogleDriveClient

service_mapper = {
    'customer': GenerateCustomerInvoicesService,
}

logger = get_task_logger(__name__)

@shared_task
def generate_customer_invoices(month: datetime.date):

    drive = GoogleDriveClient()

    employer_repo = EmployerRepository()
    customer_repo = CustomerRepository()
    work_repo = WorkRepository()
    invoice_repo = CustomerInvoiceRepository()

    start_date = month.replace(day=1)
    end_date = (
        month.replace(month=month.month % 12 + 1, day=1)
        - datetime.timedelta(days=1)
    )

    service = GenerateCustomerInvoicesService(
        start_date=start_date,
        end_date=end_date,
        drive=drive,
        employer_repo=employer_repo,
        customer_repo=customer_repo,
        work_repo=work_repo,
        invoice_repo=invoice_repo
    )
    service.execute()
    logger.info(
        f'Generated customer invoices, '
        f'start_date: {start_date}, end_date: {end_date}'
    )

@shared_task
def restore_customer_invoices():
    drive = GoogleDriveClient()
    repo = CustomerInvoiceRepository()
    service = RestoreCustomerInvoicesService(drive=drive, repo=repo)
    service.execute()
    logger.info('Invoices restored from Google Drive to database.')

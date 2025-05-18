import datetime
import os
import io
import json
import shutil

from django.conf import settings
from django.db.models import QuerySet
from docxtpl import DocxTemplate

from .engine import (
    DocxGenerator,
    Contractor,
    Address,
    BankAccount,
    Client,
    Content,
    Item,
    Contact, Context
)
from .drive import GoogleDriveClient
from .models import Work
from .repositories import (
    EmployersRepository,
    CustomersRepository,
    WorkRepository,
    CustomerInvoiceRepository,
    EmployeesRepository
)


class InitDatabaseService:

    def __init__(
            self,
            drive: GoogleDriveClient,
            customers_repo: CustomersRepository,
            employees_repo: EmployeesRepository,
            employers_repo: EmployersRepository,
    ):
        self.drive = drive

        self.repositories = {
            'customers': customers_repo,
            'employees': employees_repo,
            'employers': employers_repo
        }

        self.folder_path = f'{settings.BASE_DIR}/invoices/data'

    def execute(self):
        for name in self.repositories:
            self.clean_up(name)
            self.init_db(name)

    def init_db(self, key: str):
        repo = self.repositories[key]
        file_id = settings.GOOGLE_DRIVE_INIT_DATA[key]
        buffer = self.drive.download(file_id=file_id)
        data = json.loads(buffer.read().decode('utf-8'))
        buffer.close()
        repo.create_many(data)

    def clean_up(self, key: str):
        repo = self.repositories[key]
        repo.delete_all()



class CleanDatabaseService:

    def __init__(
            self,
            customer_repo: CustomersRepository,
            employee_repo: EmployeesRepository,
            employer_repo: EmployersRepository
    ):
        self.customer_repo = customer_repo
        self.employee_repo = employee_repo
        self.employer_repo = employer_repo

    def execute(self):
        self.customer_repo.delete_all()
        self.employee_repo.delete_all()
        self.employer_repo.delete_all()


class DownloadTemplateService:

    def __init__(self, drive: GoogleDriveClient):
        self.drive = drive
        self._temp_dir = 'tmp'

    def execute(self):
        self._create_temp_dir()
        self.download_templates()
        self._remove_temp_dir()

    def download_templates(self):
        for filename, file_id in settings.GOOGLE_DRIVE_DOCX_TEMPLATES.items():
            output_path = f'{self._temp_dir}/{filename}'
            buffer = self.drive.download(file_id=file_id)
            doc = DocxTemplate(buffer)
            doc.save(f'invoices/docx/{filename}.docx')

    def _create_temp_dir(self):
        os.makedirs(self._temp_dir, exist_ok=True)

    def _remove_temp_dir(self):
        shutil.rmtree(self._temp_dir)


class GenerateCustomerInvoicesService:

    def __init__(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            drive: GoogleDriveClient,
            employer_repo: EmployersRepository,
            customer_repo: CustomersRepository,
            work_repo: WorkRepository,
            invoice_repo: CustomerInvoiceRepository,
            last_invoice_number: str
    ):
        self.start_date = start_date
        self.end_date = end_date

        self.drive = drive

        self.employer_repo = employer_repo
        self.customer_repo = customer_repo
        self.work_repo = work_repo
        self.invoice_repo = invoice_repo

        self.last_invoice_number = last_invoice_number

    def execute(self):
        employer = self.employer_repo.get()
        works = self.work_repo.get_for_invoice(self.start_date, self.end_date)
        customers = self.customer_repo.get_for_invoice(
            self.start_date,
            self.end_date,
            works=works
        )

        folder_id = self.drive.create_folder_structure(
            f'customers/{self.end_date.year}/{self.end_date.month:02d}'
        )

        contractor = self._build_contractor(name=employer.name, data=employer.data)

        # FIXME
        invoice_number = int(self.last_invoice_number)

        template = self.download_template()

        invoices_to_create = []
        for number, customer in enumerate(customers, start=invoice_number+1):
            client = self._build_client(data=customer.data)
            content = self._build_content(
                works=works,
                data=customer.data,
                invoice_number=number
            )
            filename = self._create_filename(customer.name)

            context = Context(
                client=client,
                contractor=contractor,
                content=content
            )

            generator = DocxGenerator(data=context.dict(), template=template)

            with io.BytesIO() as buffer:
                generator.generate(buffer)
                file_id = self.drive.upload(
                    file=buffer,
                    filename=filename,
                    parent_id=folder_id
                )
                self.drive.convert_docx_to_pdf(
                    file_id=file_id,
                    filename=filename,
                    folder_id=folder_id
                )

            invoice = self.invoice_repo.create_draft(
                customer_id=customer.id,
                data=context.dict()
            )

            invoices_to_create.append(invoice)

        # TODO list all invoices for the month
        invoices = self.invoice_repo.get_by_month(year=self.end_date.year, month=self.end_date.month)
        mapper = {
            invoice.customer_id: invoice
            for invoice in invoices
        }
        # iterate over draft and split which ones has to be created and which one has to be updated
        invoices_to_update = []
        for invoice in invoices_to_create:
            if invoice.customer_id in mapper:
                invoice = mapper[invoice.customer_id]
                invoices_to_update.append(invoice)
                invoices_to_create.remove(invoice)

        self.invoice_repo.create_many(invoices_to_create)
        self.invoice_repo.update_many(invoices_to_update)

    @staticmethod
    def _create_filename(name: str) -> str:
        customer_name = (
            name
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )
        return f'{customer_name}.docx'

    @staticmethod
    def _build_contractor(name: str, data: dict) -> Contractor:
        return Contractor(
            name=name,
            company=data['company'],
            number=f'St.Nr. {data["st_nr"]} USt-Id.Nr: {data["vat_id"]}',
            address=Address(
                street_name=data['address']['street_name'],
                zip_code=data['address']['zip_code'],
                city=data['address']['city']
            ),
            bank_account=BankAccount(
                bank_name=data['bank_account']['bank_name'],
                iban=data['bank_account']['iban'],
                bic=data['bank_account']['bic']
            ),
            contact=Contact(
                email=data['contact']['email'],
                phone=data['contact']['phone']
            )
        )

    @staticmethod
    def _build_client(data: dict) -> Client:
        number = f"St.Nr.{data['st_nr']}" if data.get('st_nr') else None
        return  Client(
            name=data['name'],
            address=Address(
                street_name=data['address']['street_name'],
                zip_code=data['address']['zip_code'],
                city=data['address']['city']
            ),
            number=number
        )

    def _build_content(
            self,
            data: dict,
            works: QuerySet[Work],
            invoice_number: int
    ) -> Content:
        grouper = {}
        for work in works:
            if work.date not in grouper:
                grouper[work.date] = {'price': work.total_price, 'hours': work.hours}
            else:
                grouper[work.date]['price'] += work.total_price
                grouper[work.date]['hours'] += work.hours

        items = [
            Item(date=date, price=values['price'], hours=values['hours'])
            for date, values in grouper.items()
        ]

        return Content(
            items=items,
            invoice_number=invoice_number,
            issue_date=self.end_date,
            extended=data.get('wants_extended_invoice', False),
            vat=data.get('is_vat', False),
            year=self.end_date.year,
            month=self.end_date.month,
            note=data['note'],
        )

    def download_template(self) -> io.BytesIO:
        template_file_id = settings.GOOGLE_DRIVE_DOCX_TEMPLATES['customers']
        return self.drive.download(file_id=template_file_id)


class RestoreCustomerInvoicesService:

    def __init__(
            self,
            drive: GoogleDriveClient,
            repo: CustomerInvoiceRepository,
    ):
        self.drive = drive
        self.repo = repo
        self.template = settings.BASE_DIR / settings.CUSTOMER_TEMPLATE_PATH

    def execute(self):

        invoices = self.repo.get_all()

        for invoice in invoices:
            generator = DocxGenerator(data=invoice.data, template=self.template)

            with io.BytesIO() as buffer:
                generator.generate(buffer)
                filename = self._create_filename(invoice.customer.name)
                backup_filepath = self._create_backup_folder_structure(
                    data=invoice.data,
                )
                folder_id = self.drive.create_folder_structure(backup_filepath)
                file_id = self.drive.upload(
                    file=buffer,
                    filename=filename,
                    parent_id=folder_id
                )
                self.drive.convert_docx_to_pdf(
                    file_id=file_id,
                    filename=filename,
                    folder_id=folder_id
                )

    @staticmethod
    def _create_filename(name: str) -> str:
        customer_name = (
            name
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )
        return f'{customer_name}.docx'

    @staticmethod
    def _create_backup_folder_structure(data: dict) -> str:
        issue_date = data.get('cnt', {}).get('issue_date')
        date = datetime.datetime.strptime(issue_date, '%d.%m.%Y')
        year = date.strftime('%Y')
        month = date.strftime('%m')
        return f'backup/customers/{year}/{month}'

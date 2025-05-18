import dataclasses
import io
import datetime

from docxtpl import DocxTemplate

from .utils import MONTH_MAPPER


@dataclasses.dataclass
class Address:
    street_name: str
    city: str
    zip_code: str

    def dict(self) -> dict:
        return {
            'street': self.street_name,
            'city': self.city,
            'code': self.zip_code
        }


@dataclasses.dataclass
class BankAccount:
    bank_name: str
    iban: str
    bic: str

    def dict(self) -> dict:
        return {
            'bank_name': self.bank_name,
            'iban': self.iban,
            'bic': self.bic
        }


@dataclasses.dataclass
class Contact:
    email: str
    email: str
    phone: str

    def dict(self) -> dict:
        return {
            'phone': f'Tel.Pl: {self.phone}',
            'email': f'Email: {self.email}'
        }


@dataclasses.dataclass
class Contractor:
    company: str
    name: str
    number: str
    address: Address
    bank_account: BankAccount
    contact: Contact | None = None

    def dict(self) -> dict:
        data = {
            'company': self.company,
            'name': self.name,
            'number': self.number,
            'a': self.address.dict(),
            'bank_account': self.bank_account.dict(),
        }
        if self.contact:
            data['contact'] = self.contact.dict()
        return data


@dataclasses.dataclass
class Client:
    name: str
    address: Address
    number: str | None = None

    def dict(self) -> dict:
        data = {
            'name': self.name,
            'a': self.address.dict()
        }
        if self.number:
            data['number'] = self.number
        return data


@dataclasses.dataclass
class Item:
    hours: int
    price: int
    date: datetime.date

    def dict(self) -> dict:
        hours = int(self.hours) if self.hours.is_integer() else self.hours
        return {
            'hours': f"{hours} Std",
            'total': f"{self.price / 100:.2f} €",
            'date': self.date.strftime('%d.%m.%Y')
        }


@dataclasses.dataclass
class Content:
    invoice_number: int
    issue_date: datetime.date
    items: list[Item]
    note: str

    year: int
    month: int

    extended: bool = False
    vat: bool = False

    def __post_init__(self):
        self.netto_amount = sum(item.price for item in self.items) / 100
        self.tax_amount = self.netto_amount * 0.19
        self.brutto_amount = self.netto_amount + self.tax_amount

    def dict(self) -> dict:
        return {
            'invoice_number': self.invoice_number,
            'issue_date': self.issue_date.strftime('%d.%m.%Y'),
            'items_': [item.dict() for item in self.items],
            'netto': f"{self.netto_amount:.2f} €",
            'brutto': f"{self.brutto_amount:.2f} €",
            'tax': f"{self.tax_amount:.2f} €",
            'year': self.year,
            'month': MONTH_MAPPER[self.month],
            'extended': self.extended,
            'vat': self.vat,
            'note': self.note,
        }

@dataclasses.dataclass
class Context:
    client: Client
    contractor: Contractor
    content: Content

    def dict(self) -> dict:
        return {
            'cl': self.client.dict(),
            'co': self.contractor.dict(),
            'cnt': self.content.dict()
        }


class DocxGenerator:

    def __init__(self, data: dict, template: io.BytesIO):
        self.data = data
        self.template = template

    def generate(self, output: io.BytesIO):
        doc = DocxTemplate(self.template)
        doc.render(context=self.data)
        doc.save(output)

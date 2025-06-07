from core.base_repository import BaseRepository
from works.models import Employee, Customer, Address, Work, BankAccount


class EmployeeRepository(BaseRepository):
    _model = Employee


class CustomerRepository(BaseRepository):
    _model = Customer


class AddressRepository(BaseRepository):
    _model = Address


class BankAccountRepository(BaseRepository):
    _model = BankAccount


class WorkRepository(BaseRepository):
    _model = Work

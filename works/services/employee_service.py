import json

from django.db import transaction

from works.models import Employee, Address, BankAccount
from works.repositories import (
    EmployeeRepository,
    AddressRepository,
    BankAccountRepository
)

class EmployeeService:
    def __init__(
            self,
            employee_repository: EmployeeRepository,
            address_repository: AddressRepository,
            bank_account_repository: BankAccountRepository
    ):
        self._employee_repository = employee_repository
        self._address_repository = address_repository
        self._bank_account_repository = bank_account_repository

    def get_all(self) -> list[Employee]:
        return self._employee_repository.get_list()

    @transaction.atomic
    def migrate(self) -> None:
        self._employee_repository.drop_all()
        self._address_repository.drop_all()
        self._bank_account_repository.drop_all()

        with open('employees.json', 'r') as file:
            employees_data = json.load(file)

        employees_to_create = []
        addresses_to_create = []
        bank_accounts_to_create = []
        for employee_data in employees_data:
            address = Address(
                street_address=employee_data['address']['street_address'],
                postal_code=employee_data['address']['postal_code'],
                city=employee_data['address']['city'],
            )

            bank_account = BankAccount(
                bank_name=employee_data['bank_account']['bank_name'],
                iban=employee_data['bank_account']['iban'],
                bic=employee_data['bank_account']['bic'],
            )

            employee = Employee(
                name=employee_data['name'],
                code=employee_data['code'],
                company_name=employee_data['company_name'],
                metadata=employee_data['metadata'],
                hourly_rate=employee_data['hourly_rate'],
                address=address,
                bank_account=bank_account,
            )

            employees_to_create.append(employee)
            addresses_to_create.append(address)
            bank_accounts_to_create.append(bank_account)

        Address.objects.bulk_create(addresses_to_create)
        BankAccount.objects.bulk_create(bank_accounts_to_create)
        self._employee_repository.bulk_create(employees_to_create)

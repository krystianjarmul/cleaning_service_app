from works.repositories import (
    CustomerRepository,
    AddressRepository,
    BankAccountRepository
)
from works.repositories import EmployeeRepository
from works.services.customer_service import CustomerService
from works.services.employee_service import EmployeeService


class ServiceFactory:

    @classmethod
    def create_employee_service(cls) -> EmployeeService:
        return EmployeeService(
            employee_repository=EmployeeRepository(),
            address_repository=AddressRepository(),
            bank_account_repository=BankAccountRepository()
        )

    @classmethod
    def create_customer_service(cls) -> CustomerService:
        return CustomerService(CustomerRepository())


from django.db import transaction

from works.models import Customer
from works.repositories import CustomerRepository


class CustomerService:
    def __init__(self, customer_repository: CustomerRepository):
        self._customer_repository = customer_repository

    def get_all(self) -> list[Customer]:
        return self._customer_repository.get_list()

    @transaction.atomic
    def migrate(self) -> None:
        self._customer_repository.drop_all()

        # with open('customers.json', 'r') as file:
        #     customers_data = json.load(file)
        #
        # customers_to_create = []
        # addresses_to_create = []
        # for data in customers_data:
        #     customer = Customer(
        #         name=data['name'],
        #         code=data['code'],
        #         company_name=data['company_name'],
        #         specifications=data['specifications'],
        #         hourly_rate=data['hourly_rate'],
        #     )
        #     # address = CustomerAddress(
        #     #     street_address=data['address']['street_address'],
        #     #     postal_code=data['address']['postal_code'],
        #     #     city=data['address']['city'],
        #     #     employee=data,
        #     # )
        #
        #     customers_to_create.append(customer)
        #     # addresses_to_create.append(address)
        #
        # self._customer_repository.bulk_create(customers_to_create)
        # CustomerAddress.objects.bulk_create(addresses_to_create)

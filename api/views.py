import pprint

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from api.serializers import EmployeeSerializer, CustomerSerializer
from works.models import Employee
from works.service_factory import ServiceFactory


class EmployeesView(APIView):

    def get(self, request: Request) -> Response:
        service = ServiceFactory.create_employee_service()
        employees = service.get_all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CustomersView(APIView):

    def get(self, request: Request) -> Response:
        service = ServiceFactory.create_customer_service()
        customers = service.get_all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

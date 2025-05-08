import datetime

from django.db import models


class Employer(models.Model):

    name = models.CharField(
        max_length=100,
    )

    data = models.JSONField(default=dict)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class Employee(models.Model):

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]

    name = models.CharField(
        max_length=100,
    )

    code = models.CharField(
        max_length=2,
        null=True
    )

    data = models.JSONField(default=dict)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.code} | {self.name}"


class Customer(models.Model):

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    name = models.CharField(
        max_length=100,
    )

    price = models.IntegerField()

    data = models.JSONField(default=dict)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self) -> str:
        return self.name


class Work(models.Model):

    class Meta:
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['employee']),
            models.Index(fields=['date'])
        ]

    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE,
        related_name='works'
    )

    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='works',
    )

    hours = models.FloatField()

    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self) -> str:
        return f"Work {self.date} | {self.customer.name} | {self.employee.name}"


class CustomerInvoice(models.Model):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )

    data = models.JSONField(default=dict)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def number(self):
        return self.data.get('cnt', {}).get('invoice_number')

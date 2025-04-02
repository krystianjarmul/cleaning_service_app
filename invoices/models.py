from django.db import models


class Employee(models.Model):

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_employer'])
        ]

    name = models.CharField(
        max_length=100,
    )

    is_employer = models.BooleanField(default=False)

    data = models.JSONField(default=dict)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name 


class Customer(models.Model):

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    name = models.CharField(
        max_length=100,
    )

    data = models.JSONField(default=dict)

    price = models.IntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
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

    hours = models.IntegerField()

    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self) -> str:
        return f"Work {self.date} | {self.customer.name} | {self.employee.name}"


class Invoice(models.Model):

    class Type(models.TextChoices):
        EMPLOYEE = "employee"
        CUSTOMER = "customer"

    filename = models.CharField(
        max_length=100
    )

    type = models.CharField(
        max_length=10,
        choices=Type.choices,
        default=Type.CUSTOMER
    )

    file = models.FileField(upload_to="invoices/")

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

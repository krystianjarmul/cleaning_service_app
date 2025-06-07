from django.db import models


class Address(models.Model):

    street_address = models.CharField(
        max_length=100
    )

    postal_code = models.CharField(
        max_length=6
    )

    city = models.CharField(
        max_length=50
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.street_address}, {self.postal_code}, {self.city}"


class BankAccount(models.Model):

    iban = models.CharField(
        max_length=30
    )

    bank_name = models.CharField(
        max_length=100
    )

    bic = models.CharField(
        max_length=11,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.bank_name} - ({self.bic})"


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
    )

    hourly_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=12.00
    )

    company_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    metadata = models.JSONField(default=dict)

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees'
    )

    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees'
    )

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

    metadata = models.JSONField(default=dict)

    invoice_name = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    hourly_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.00
    )

    note = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    address_id = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='customers'
    )

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
        related_name='works'
    )

    hours = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

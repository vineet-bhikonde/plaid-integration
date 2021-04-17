from django.contrib.auth.models import User
from django.db import models


class AvailableProduct(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BilledProduct(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Item(models.Model):
    item = models.CharField(max_length=100, null=False)
    access_token = models.CharField(max_length=200, null=False)
    consent_expiration_time = models.DateTimeField(null=True)
    error = models.CharField(max_length=100, null=True)
    institution_id = models.CharField(max_length=10, null=True)
    update_type = models.CharField(max_length=50, null=True)
    webhook = models.CharField(max_length=100, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    available_products = models.ManyToManyField(AvailableProduct)
    billed_products = models.ManyToManyField(BilledProduct)

    def __str__(self):
        return self.user.username + "\t" + self.item


class Balance(models.Model):
    available = models.FloatField(default=0.0, null=True)
    current = models.FloatField(default=0.0, null=True)
    iso_currency_code = models.CharField(max_length=10)
    limit = models.FloatField(null=True)
    unofficial_currency_code = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.account.account_id + '\t' + self.account.name


class Account(models.Model):
    account_id = models.CharField(max_length=100, null=False, unique=True)
    mask = models.CharField(max_length=10)
    name = models.CharField(max_length=50, null=False)
    official_name = models.CharField(max_length=100, null=True)
    subtype = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    balances = models.OneToOneField(Balance, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return 'Item id:' + self.item.item + '\t Account Id:' + self.account_id


class TransactionCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TransactionLocation(models.Model):
    address = models.CharField(max_length=500, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=50, null=True)
    lat = models.CharField(max_length=50, null=True)
    lon = models.CharField(max_length=50, null=True)
    postal_code = models.CharField(max_length=50, null=True)
    region = models.CharField(max_length=50, null=True)
    store_number = models.CharField(max_length=50, null=True)


class TransactionPaymentMeta(models.Model):
    by_order_of = models.CharField(max_length=50, null=True)
    payee = models.CharField(max_length=50, null=True)
    payer = models.CharField(max_length=50, null=True)
    payment_method = models.CharField(max_length=50, null=True)
    payment_processor = models.CharField(max_length=50, null=True)
    ppd_id = models.CharField(max_length=50, null=True)
    reason = models.CharField(max_length=50, null=True)
    reference_number = models.CharField(max_length=50, null=True)


class TransactionDetail(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    account_owner = models.CharField(max_length=100, null=True)
    amount = models.FloatField(default=0.0)
    authorized_date = models.DateField(null=True)
    authorized_date_time = models.DateTimeField(null=True)
    category = models.ManyToManyField(TransactionCategory)
    category_id = models.IntegerField(default=0)
    date = models.DateField(null=True)
    datetime = models.DateTimeField(null=True)
    iso_currency_code = models.CharField(max_length=10, null=True)
    location = models.OneToOneField(TransactionLocation, on_delete=models.CASCADE)
    merchant_name = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=50, null=True)
    payment_channel = models.CharField(max_length=20, null=True)
    payment_meta = models.OneToOneField(TransactionPaymentMeta, on_delete=models.CASCADE)
    pending = models.BooleanField(default=False)
    pending_transaction_id = models.BigIntegerField(null=True)
    transaction_code = models.IntegerField(null=True)
    transaction_id = models.CharField(max_length=500, unique=True, default=0)
    transaction_type = models.CharField(max_length=50, null=True)
    unofficial_currency_code = models.CharField(max_length=10, null=True)

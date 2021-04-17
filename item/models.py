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

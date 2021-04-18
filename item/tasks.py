import datetime

import plaid
from celery import shared_task
from rest_framework.exceptions import ValidationError

from item.models import Item, AvailableProduct, BilledProduct, TransactionDetail, Account
from item.serializers import AccountSerializer, TransactionDetailSerializer, ItemSerializer
from plaid_integration.PlaidClient import PlaidClient

client = PlaidClient.get_instance()


@shared_task
def fetch_item_meta_data(item):
    item_object = Item.objects.get(item=item)
    try:
        item_response = client.Item.get(item_object.access_token)
    except plaid.errors.PlaidError as e:
        return "Plaid error occurred."
    item_serializer = ItemSerializer(instance=item_object, data=item_response['item'],
                                     context={'available_products': item_response['item']['available_products'],
                                                                    'billed_products': item_response['item']['billed_products']
                                                                    })
    item_serializer.is_valid(raise_exception=True)
    item_serializer.save()
    return "Item meta data updated"


@shared_task
def fetch_item_account_data(item):
    item_object = Item.objects.get(item=item)
    try:
        accounts_response = client.Accounts.get(item_object.access_token)
    except plaid.errors.PlaidError as e:
        return "Plaid error occurred."
    for account in accounts_response['accounts']:
        try:
            account_serializer = AccountSerializer(context={'item': item_object}, data=account)
            account_serializer.is_valid(raise_exception=True)
            account_serializer.save()
        except Exception as error:
            account_object = Account.objects.get(account_id=account['account_id'])
            account_update_serializer = AccountSerializer(instance=account_object, data=account)
            account_update_serializer.is_valid(raise_exception=True)
            account_update_serializer.save()
    return "Account details updated"


@shared_task
def delete_transactions(deleted_transactions):
    for transaction_id in deleted_transactions:
        TransactionDetail.objects.filter(transaction_id=transaction_id).delete()

    return "Transactions Deleted"


@shared_task
def update_transactions(item_id):
    start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-15))
    end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
    item = Item.objects.get(item=item_id)
    try:
        transactions_response = client.Transactions.get(item.access_token, start_date, end_date)
    except plaid.errors.PlaidError as e:
        return "Plaid error occurred while fetching transactions"

    # Updating transaction details
    for transaction in transactions_response['transactions']:
        try:
            transaction_serializer = TransactionDetailSerializer(data=transaction)
            transaction_serializer.is_valid(raise_exception=True)
            transaction_serializer.save()
        except ValidationError:
            transaction_object = TransactionDetail.objects.get(
                transaction_id=transaction['transaction_id'])
            serializer = TransactionDetailSerializer(instance=transaction_object, data=transaction)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    # Updating account and balance details
    for account in transactions_response['accounts']:
        account_object = Account.objects.get(account_id=account['account_id'])
        account_update_serializer = AccountSerializer(instance=account_object, data=account)
        account_update_serializer.is_valid(raise_exception=True)
        account_update_serializer.save()
    return "Transactions Updated"

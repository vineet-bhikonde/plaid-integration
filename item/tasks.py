import datetime

import plaid
from celery import shared_task

from item.models import Item, AvailableProduct, BilledProduct, TransactionDetail
from item.serializers import AccountSerializer
from plaid_integration.PlaidClient import PlaidClient

client = PlaidClient.get_instance()


@shared_task
def fetch_item_meta_data(item):
    item_object = Item.objects.get(item=item)
    item_response = client.Item.get(item_object.access_token)
    for available_product in item_response['item']['available_products']:
        available_product_object, created = AvailableProduct.objects.get_or_create(name=available_product)
        item_object.available_products.add(available_product_object)
    for billed_product in item_response['item']['billed_products']:
        billed_product_object, created = BilledProduct.objects.get_or_create(name=billed_product)
        item_object.billed_products.add(billed_product_object)
    return None


@shared_task
def fetch_item_account_data(item):
    item_object = Item.objects.get(item=item)
    try:
        accounts_response = client.Accounts.get(item_object.access_token)
    except plaid.errors.PlaidError as e:
        return
    serializer = AccountSerializer(many=True, context={'item': item_object}, data=accounts_response['accounts'])
    if serializer.is_valid():
        serializer.save()
    else:
        print(serializer.errors)
    return


@shared_task
def delete_transactions(deleted_transactions):

    for transaction_id in deleted_transactions:
        TransactionDetail.objects.filter(transaction_id=transaction_id).delete()

    return "Transactions Deleted"


@shared_task
def update_transactions(item_id, updated_transactions):
    pass

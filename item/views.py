import datetime

import plaid
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from item.models import Item, Account, TransactionDetail
from plaid_integration.PlaidClient import PlaidClient
from .serializers import ItemAccountSerializer, AccessTokenRequestSerializer, \
    ItemTransactionSerializer, TransactionDetailSerializer, ItemSerializer
from .tasks import fetch_item_meta_data, fetch_item_account_data, delete_transactions, \
    insert_or_update_transactions

client = PlaidClient.get_instance()


class AccessTokenApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        access_token_request_serializer = AccessTokenRequestSerializer(data=request.data)
        access_token_request_serializer.is_valid(raise_exception=True)
        try:
            exchange_token = client.Item.public_token.exchange(access_token_request_serializer.data.get('public_token'))
        except plaid.errors.PlaidError as e:
            if e.code == 'INVALID_PUBLIC_TOKEN':
                return Response(data={'error': e.message}, status=401)
            else:
                return Response(data={'error': e.message}, status=400)
        item, created = Item.objects.update_or_create(
            item=exchange_token['item_id'],
            defaults={'user': request.user, 'access_token': exchange_token['access_token']})
        fetch_item_meta_data.delay(item.item)
        fetch_item_account_data.delay(item.item)
        return Response(exchange_token)


class AccountApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        item = Item.objects.filter(user=request.user)
        if not item:
            return Response(data={'error': 'No Items available.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ItemAccountSerializer(item, many=True)
        return Response(serializer.data)


class AccountTransactionApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        item = Item.objects.filter(user=request.user)
        if not item:
            return Response(data={'error': 'No Items available to display transactions.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ItemTransactionSerializer(item, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def post(self, request):
        items = Item.objects.filter(user=request.user)
        if items:
            item_serializer = ItemSerializer(many=True, data=items)
            item_serializer.is_valid()
            insert_or_update_transactions.delay(item_serializer.data)
        else:
            return Response(data={'error': 'No items for fetching transactions.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Fetching transaction data.'}, status=status.HTTP_201_CREATED)


class TransactionsWebhook(APIView):

    @transaction.atomic
    def post(self, request):
        data = request.data

        webhook_type = data['webhook_type']
        webhook_code = data['webhook_code']

        if webhook_type == 'TRANSACTIONS':
            item_id = data['item_id']
            if webhook_code == 'TRANSACTIONS_REMOVED':
                delete_transactions.delay(data['removed_transactions'])
            else:
                if data['new_transactions'] is not 0:
                    item_serializer = ItemSerializer(data=Item.objects.get(item=item_id))
                    item_serializer.is_valid()
                    insert_or_update_transactions.delay(item_serializer.data, True)
                else:
                    print("No New Transactions")

        return Response("Webhook received", status=status.HTTP_202_ACCEPTED)


class WebhookTestView(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        item = Item.objects.filter(user=request.user)
        access_token = item[0].access_token

        res = client.Sandbox.item.fire_webhook(access_token, 'DEFAULT_UPDATE')

        print("Webhook fired: ", res['webhook_fired'])

        return Response({"message": "Webhook fired"}, status=status.HTTP_200_OK)


class WebhookRegistrationView(APIView):

    def post(self, request):
        base_url = request.data['base_url']
        # For ease first item of the user is considered for registering
        item = Item.objects.filter(user=request.user)
        access_token = item[0].access_token
        try:
            res = client.Item.webhook.update(access_token, webhook=base_url + "/api/v1/item/webhook/transactions")
        except plaid.errors.PlaidError as e:
            Response({'error': 'Failed to register webhook'})
        return Response({'message': 'Webhook registered'}, status=status.HTTP_201_CREATED)

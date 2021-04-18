import datetime

import plaid
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from item.models import Item, Account, TransactionDetail
from plaid_integration.PlaidClient import PlaidClient
from .serializers import ItemAccountSerializer, AccessTokenRequestSerializer, \
    ItemTransactionSerializer, TransactionDetailSerializer
from .tasks import fetch_item_meta_data, fetch_item_account_data, delete_transactions, update_transactions

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
            return Response(data={'error': 'No Items available.'}, status=400)
        serializer = ItemAccountSerializer(item, many=True)
        return Response(serializer.data)


class AccountTransactionApiView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        item = Item.objects.filter(user=request.user)
        if not item:
            return Response(data={'error': 'No Items available to display transactions.'}, status=400)
        serializer = ItemTransactionSerializer(item, many=True)
        return Response(serializer.data)

    def post(self, request):
        start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-15))
        end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
        try:
            items = Item.objects.filter(user=request.user)
            if items:
                for item in items:
                    transactions_response = client.Transactions.get(item.access_token, start_date, end_date)
                    for transaction in transactions_response['transactions']:
                        try:
                            transaction_serializer = TransactionDetailSerializer(data=transaction)
                            transaction_serializer.is_valid(raise_exception=True)
                            transaction_serializer.save()
                        except Exception:
                            transaction_object = TransactionDetail.objects.get(
                                transaction_id=transaction['transaction_id'])
                            serializer = TransactionDetailSerializer(instance=transaction_object, data=transaction)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
        except plaid.errors.PlaidError as e:
            return Response(data={'error': e.message}, status=400)
        return Response(data={'message': 'Transaction data fetched.'}, status=201)


class TransactionsWebhook(APIView):

    def post(self, request):
        data = request.data

        webhook_type = data['webhook_type']
        webhook_code = data['webhook_code']

        if webhook_type == 'TRANSACTIONS':
            item_id = data['item_id']
            if webhook_code == 'TRANSACTIONS_REMOVED':
                delete_transactions.delay(data['removed_transactions'])
            else:
                new_transactions = data['new_transactions']
                # if new_transactions is not 0:
                update_transactions.delay(item_id)
                # else:
                #     print("No New Transactions")

        return Response("Webhook received", status=status.HTTP_202_ACCEPTED)


class WebhookTestView(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        item = Item.objects.filter(user=request.user)
        access_token = item[0].access_token

        # fire a DEFAULT_UPDATE webhook for an item
        res = client.Sandbox.item.fire_webhook(access_token, 'DEFAULT_UPDATE')

        print("Webhook fired: ", res['webhook_fired'])

        return Response({"message": "Webhook fired"}, status=status.HTTP_200_OK)


class WebhookRegistrationView(APIView):

    def post(self, request):
        item = Item.objects.filter(user=request.user)
        access_token = item[0].access_token
        try:
            res = client.Item.webhook.update(access_token, webhook="https://671ea3cbf79b.ngrok.io/api/v1/item/webhook/transactions")
        except plaid.errors.PlaidError as e:
            print(e)
        print(res)
        return Response({'message':'Webhook registered'}, status=status.HTTP_201_CREATED)

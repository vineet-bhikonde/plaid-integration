import datetime

import plaid
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from item.models import Item, Account
from .serializers import AccountSerializer, ItemSerializer, ItemAccountSerializer, AccessTokenRequestSerializer, \
    ItemTransactionSerializer, TransactionDetailSerializer
from .tasks import fetch_item_meta_data, fetch_item_account_data

client = plaid.Client(
            client_id="6077aff00b1c9e00111702d8",
            secret="842032c8317c41824f993a2c23d81f",
            environment="sandbox",
            api_version="2020-09-14"
        )


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
                    transaction_serializer = TransactionDetailSerializer(many=True,
                                                                         data=transactions_response['transactions'])
                    transaction_serializer.is_valid(raise_exception=True)
                    transaction_serializer.save()
        except plaid.errors.PlaidError as e:
            return Response(data={'error': e.message}, status=400)
        return Response(data={'message': 'Transaction data fetched.'}, status=201)

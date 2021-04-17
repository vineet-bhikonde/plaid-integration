import plaid
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from item.models import Item
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
        public_token = request.data['public_token']
        try:
            exchange_token = client.Item.public_token.exchange(public_token)
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

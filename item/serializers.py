from rest_framework import serializers

from core.serializers import UserSerializer
from item.models import Account, Balance, AvailableProduct, BilledProduct, Item


class AvailableProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = AvailableProduct
        fields = ['name']


class BilledProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = BilledProduct
        fields = ['name']


class BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Balance
        fields = ['available', 'current', 'iso_currency_code', 'limit', 'unofficial_currency_code']


class AccountSerializer(serializers.ModelSerializer):
    balances = BalanceSerializer()

    class Meta:
        model = Account
        fields = ['account_id', 'mask', 'name', 'official_name', 'subtype', 'type', 'balances']

    def create(self, validated_data):
        balance = validated_data.pop('balances')
        validated_data['item'] = self.context.get('item')
        balance_object = Balance.objects.create(**balance)
        account = Account.objects.create(balances=balance_object, **validated_data)
        return account


class ItemSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    available_products = serializers.StringRelatedField(many=True, read_only=True)
    billed_products = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ['item', 'access_token', 'consent_expiration_time', 'error', 'institution_id',
                  'user', 'available_products', 'billed_products', 'update_type', 'webhook', 'account_set']
        depth = 2


class ItemAccountSerializer(serializers.Serializer):
    item_id = serializers.CharField(source='item')
    account = AccountSerializer(many=True, source='account_set')


class AccessTokenRequestSerializer(serializers.Serializer):
    public_token = serializers.CharField(max_length=500)

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


class ItemsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    available_products = AvailableProductSerializer(many=True, read_only=True)
    billed_products = BilledProductSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ['item', 'access_token', 'consent_expiration_time', 'error', 'institution_id',
                  'user', 'available_products', 'billed_products', 'update_type', 'webhook']
        depth = 1


class BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Balance
        fields = ['available', 'current', 'iso_currency_code', 'limit', 'unofficial_currency_code']


class AccountSerializer(serializers.ModelSerializer):
    balances = BalanceSerializer(source='account')
    item = ItemsSerializer(read_only=True)

    class Meta:
        model = Account
        fields = ['account_id', 'mask', 'name', 'official_name', 'subtype', 'type', 'item', 'balances']

    def create(self, validated_data):
        balance = validated_data.pop('account')
        validated_data['item'] = self.context.get('item')
        # account_id = validated_data.get('account_id')
        # account, created = Account.objects.update_or_create(account_id=validated_data.get('account_id'),
        #                                             defaults=validated_data)
        account = Account.objects.create(**validated_data)
        balance['account'] = account
        Balance.objects.create(**balance)
        return account

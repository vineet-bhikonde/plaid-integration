from rest_framework import serializers

from core.serializers import UserSerializer
from item.models import Account, Balance, AvailableProduct, BilledProduct, Item, TransactionCategory, TransactionDetail, \
    TransactionLocation, TransactionPaymentMeta


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




class TransactionCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionCategory
        fields = ['name']


class TransactionLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLocation
        exclude = ['id']


class TransactionPaymentMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionPaymentMeta
        exclude = ['id']


class TransactionDetailSerializer(serializers.ModelSerializer):
    category = serializers.ListField(write_only=True)
    location = TransactionLocationSerializer()
    payment_meta = TransactionPaymentMetaSerializer()
    account_id = serializers.CharField(write_only=True)

    class Meta:
        model = TransactionDetail
        exclude = ['id', 'account']

    def create(self, validated_data):
        payment_meta = validated_data.pop('payment_meta')
        location = validated_data.pop('location')
        account_id = validated_data.pop('account_id')
        category_details = validated_data.pop('category')
        payment_meta_object = TransactionPaymentMeta.objects.create(**payment_meta)
        location_object = TransactionLocation.objects.create(**location)
        account_object = Account.objects.get(account_id=account_id)
        transaction_detail_object = TransactionDetail.objects.create(location=location_object,
                                                                     payment_meta=payment_meta_object,
                                                                     account=account_object,
                                                                     **validated_data)
        for category in category_details:
            category_object, created = TransactionCategory.objects.get_or_create(name=category)
            transaction_detail_object.category.add(category_object)
        return transaction_detail_object


class ItemAccountSerializer(serializers.Serializer):
    item_id = serializers.CharField(source='item')
    account = AccountSerializer(many=True, source='account_set')


class AccessTokenRequestSerializer(serializers.Serializer):
    public_token = serializers.CharField(max_length=500)


class AccountTransactionSerializer(serializers.Serializer):
    account_id = serializers.CharField()
    transactions = TransactionDetailSerializer(many=True)


class ItemTransactionSerializer(serializers.Serializer):
    item_id = serializers.CharField(source='item')
    transactions = AccountTransactionSerializer(many=True, source='account_set')

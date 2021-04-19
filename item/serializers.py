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

    def update(self, instance, validated_data):
        balance = validated_data.pop('balances', None)
        if balance:
            balance_serializer = BalanceSerializer(instance=instance.balances, data=balance)
            balance_serializer.is_valid(raise_exception=True)
            balance_serializer.save()
        instance.mask = validated_data.get('mask', instance.mask)
        instance.name = validated_data.get('name', instance.name)
        instance.official_name = validated_data.get('official_name', instance.official_name)
        instance.subtype = validated_data.get('subtype', instance.subtype)
        instance.type = validated_data.get('type', instance.type)
        instance.save()
        return instance


class ItemSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    available_products = serializers.StringRelatedField(many=True, read_only=True)
    billed_products = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ['item', 'access_token', 'consent_expiration_time', 'error', 'institution_id',
                  'user', 'available_products', 'billed_products', 'update_type', 'webhook', 'account_set']
        read_only_fields = ['item', 'access_token']
        depth = 2

    def update(self, instance, validated_data):
        available_products = self.context.get('available_products', None)
        billed_products = self.context.get('billed_products', None)
        instance.consent_expiration_time = validated_data.get('consent_expiration_time', instance.consent_expiration_time)
        instance.error = validated_data.get('error', instance.error)
        instance.institution_id = validated_data.get('institution_id', instance.institution_id)
        instance.update_type = validated_data.get('update_type', instance.update_type)
        instance.webhook = validated_data.get('webhook', instance.webhook)
        if available_products:
            for available_product in available_products:
                available_product_object, created = AvailableProduct.objects.get_or_create(name=available_product)
                instance.available_products.add(available_product_object)
        if billed_products:
            for billed_product in billed_products:
                billed_product_object, created = BilledProduct.objects.get_or_create(name=billed_product)
                instance.billed_products.add(billed_product_object)
        instance.save()
        return instance


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

    def update(self, instance, validated_data):
        payment_meta = validated_data.pop('payment_meta', None)
        location = validated_data.pop('location', None)
        category_details = validated_data.pop('category', None)
        if payment_meta:
            payment_serializer = TransactionPaymentMetaSerializer(instance=instance.payment_meta, data=payment_meta)
            payment_serializer.is_valid(raise_exception=True)
            payment_serializer.save()
        if location:
            location_serializer = TransactionLocationSerializer(instance=instance.location, data=location)
            location_serializer.is_valid(raise_exception=True)
            location_serializer.save()
        instance.account_owner = validated_data.get('account_owner', instance.account_owner)
        instance.amount = validated_data.get('amount', instance.amount)
        instance.authorized_date = validated_data.get('authorized_date', instance.authorized_date)
        instance.authorized_date_time = validated_data.get('authorized_date_time', instance.authorized_date_time)
        instance.category_id = validated_data.get('category_id', instance.category_id)
        instance.date = validated_data.get('date', instance.date)
        instance.datetime = validated_data.get('datetime', instance.datetime)
        instance.iso_currency_code = validated_data.get('iso_currency_code', instance.iso_currency_code)
        instance.location = validated_data.get('location', instance.location)
        instance.merchant_name = validated_data.get('merchant_name', instance.merchant_name)
        instance.name = validated_data.get('name', instance.name)
        instance.payment_channel = validated_data.get('payment_channel', instance.payment_channel)
        instance.payment_meta = validated_data.get('payment_meta', instance.payment_meta)
        instance.pending = validated_data.get('pending', instance.pending)
        instance.pending_transaction_id = validated_data.get('pending_transaction_id', instance.pending_transaction_id)
        instance.transaction_code = validated_data.get('transaction_code', instance.transaction_code)
        instance.transaction_id = validated_data.get('transaction_id', instance.transaction_id)
        instance.transaction_type = validated_data.get('transaction_type', instance.transaction_type)
        instance.unofficial_currency_code = validated_data.get('unofficial_currency_code',
                                                               instance.unofficial_currency_code)
        instance.save()
        for category in category_details:
            category_object, created = TransactionCategory.objects.get_or_create(name=category)
            instance.category.add(category_object)
        return instance


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

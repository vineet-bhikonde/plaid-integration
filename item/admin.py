from django.contrib import admin

from item.models import Item, AvailableProduct, BilledProduct, Account, Balance, TransactionCategory, \
    TransactionLocation, TransactionPaymentMeta, TransactionDetail

admin.site.register(Item)
admin.site.register(AvailableProduct)
admin.site.register(BilledProduct)
admin.site.register(Account)
admin.site.register(Balance)
admin.site.register(TransactionCategory)
admin.site.register(TransactionLocation)
admin.site.register(TransactionPaymentMeta)
admin.site.register(TransactionDetail)

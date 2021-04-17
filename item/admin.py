from django.contrib import admin

from item.models import Item, AvailableProduct, BilledProduct, Account, Balance

admin.site.register(Item)
admin.site.register(AvailableProduct)
admin.site.register(BilledProduct)
admin.site.register(Account)
admin.site.register(Balance)

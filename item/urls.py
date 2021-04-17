from django.urls import path

from item.views import AccessTokenApiView, AccountApiView, AccountTransactionApiView

urlpatterns = [
    path('accounts', AccountApiView.as_view(), name='accounts'),
    path('access-token', AccessTokenApiView.as_view(), name='access-token'),
    path('transactions', AccountTransactionApiView.as_view(), name='transactions')
]

from django.urls import path

from item.views import AccessTokenApiView, AccountApiView, AccountTransactionApiView, TransactionsWebhook, \
    WebhookTestView, WebhookRegistrationView

urlpatterns = [
    path('accounts', AccountApiView.as_view(), name='accounts'),
    path('access-token', AccessTokenApiView.as_view(), name='access-token'),
    path('transactions', AccountTransactionApiView.as_view(), name='transactions'),
    path('webhook/transactions', TransactionsWebhook.as_view(), name='transactions-webhook'),
    path('webhook/transactions/fire', WebhookTestView.as_view(), name='webhook-transactions-fire'),
    path('webhook/register', WebhookRegistrationView.as_view(), name='webhook-registration')
]

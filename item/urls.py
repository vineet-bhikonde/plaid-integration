from django.urls import path

from item.views import AccessTokenApiView, AccountApiView

urlpatterns = [
    path('accounts', AccountApiView.as_view(), name='accounts'),
    path('access-token', AccessTokenApiView.as_view(), name='access-token'),
]

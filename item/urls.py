from django.urls import path

from item.views import AccessTokenApiView

urlpatterns = [
    path('access-token', AccessTokenApiView.as_view(), name='access-token'),
]

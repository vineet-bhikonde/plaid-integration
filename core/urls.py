from knox import views as knox_views
from .views import LoginApiView, RegisterAPIView, UserApiView
from django.urls import path

urlpatterns = [
    path('', UserApiView.as_view(), name='user'),
    path('register/', RegisterAPIView.as_view(), name='registration'),
    path('login/', LoginApiView.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
]
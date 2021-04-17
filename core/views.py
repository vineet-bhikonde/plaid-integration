from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserSerializer
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class LoginApiView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({
            "token": AuthToken.objects.create(user)[1]
        })


class UserApiView(generics.RetrieveAPIView):

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

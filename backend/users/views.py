from django.shortcuts import render
from rest_framework.response import Response
from djoser.views import UserViewSet

from users.serializers import NewUserSerializer


class NewUserViewSet(UserViewSet):
    """Переопределяет вьюсет пользователя от djoser."""

    serializer_class = NewUserSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def retrieve(self, request, *args, **kwargs):
        print('CALLED')
        if request.user.is_authenticated:
            instance = request.user
            serializer = self.get_serializer(instance)
            print(f'!!! {serializer.data}')
            return Response(serializer.data)
        return Response({
            "detail": "Authentication credentials were not provided."},
            status=401)

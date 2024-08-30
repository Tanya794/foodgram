from django.shortcuts import render
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from djoser.views import UserViewSet

from api.permissions import IsAuthorOrReadOnly
from users.serializers import NewUserSerializer


class NewUserViewSet(UserViewSet):
    """Переопределяет вьюсет пользователя от djoser."""

    serializer_class = NewUserSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_context(self):
        print('HERE')
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def retrieve(self, request, *args, **kwargs):
        print('RETRIEVE')
        user = request.user
        if user.is_authenticated:
            instance = get_object_or_404(self.get_queryset(), pk=user.id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"detail": "Пользователь не авторизован."},
                        status=status.HTTP_401_UNAUTHORIZED)

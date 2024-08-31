from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.pagination import FoodgramPagination
from api.permissions import IsAuthorOrReadOnly
from users.serializers import NewUserSerializer, UserCreateSerializer

User = get_user_model()


class NewUserViewSet(UserViewSet):
    """Переопределяет вьюсет пользователя от djoser."""

    serializer_class = NewUserSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            instance = get_object_or_404(self.get_queryset(), pk=user.id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"detail": "Пользователь не авторизован."},
                        status=status.HTTP_401_UNAUTHORIZED)


class UserGetViewSet(viewsets.ViewSet):
    """Предоставляет просмотр и создание юзера(ов)."""

    permission_classes = (AllowAny,)

    def list(self, request):
        queryset = User.objects.all().order_by('id')
        paginator = FoodgramPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = NewUserSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = NewUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = UserSerializer(user)
        return Response(response_serializer.data,
                        status=status.HTTP_201_CREATED)

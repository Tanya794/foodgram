from djoser.serializers import TokenCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.serializers import Base64ImageField


User = get_user_model()


class TokenLoginSerializer(TokenCreateSerializer):
    """Сериализатор для входа и получения токена."""

    username = None

    class Meta:
        model = User
        fields = ('email', 'password')


class LoginUserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.BooleanField(default=False, read_only=True)

    class Meta(UserSerializer.Meta):
        model = User
        fields = UserSerializer.Meta.fields + ['avatar', 'is_subscribed']

    def to_representation(self, instance):
       # дописать логику проверки подписки
 
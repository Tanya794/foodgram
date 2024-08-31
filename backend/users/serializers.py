import base64

from django.conf import settings
from djoser.serializers import TokenCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from users.models import Subscription


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Декодирует изображение из base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TokenLoginSerializer(TokenCreateSerializer):
    """Сериализатор для входа и получения токена."""

    username = None

    class Meta:
        model = User
        fields = ('email', 'password')


class NewUserSerializer(UserSerializer):
    """Сериализатор информации о пользователе."""

    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user,
                                               subscribed_to=obj).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.avatar:
            avatar_url = instance.avatar.url
            representation['avatar'] = f'{settings.BASE_URL}{avatar_url}'
        return representation


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

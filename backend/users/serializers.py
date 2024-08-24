import base64

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
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        print('WORKS')
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user,
                                               subscribed_to=obj).exists()
        return False

    def to_representation(self, instance):
        print('YES')
        representation = super().to_representation(instance)
        if instance.avatar:
            if 'request' in self.context:
                representation['avatar'] = self.context[
                    'request'].build_absolute_uri(instance.avatar.url)
            else:
                representation['avatar'] = instance.image.url
        return representation

import re

from django.core.exceptions import ValidationError


def validate_cooking_time_or_amount(value):
    """Валидация времени приготовления."""
    if value < 1:
        raise ValidationError(
            'Значение не может быть меньше 1.'
        )


def validate_slug(value):
    if not re.match(r'^[-a-zA-Z0-9_]+$', value):
        raise ValidationError(f'Недопустимый символ в слаг: {value}')

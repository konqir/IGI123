# core/validators.py
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime

def validate_age_18_plus(value):
    """
    Валидатор для проверки, что дата рождения соответствует возрасту 18+ лет.
    """
    today = timezone.localdate()
    
    eighteenth_birthday_this_year = value.replace(year=value.year + 18)

    if eighteenth_birthday_this_year > today:
        raise ValidationError(
            'Возраст должен быть 18 лет или старше.',
            code='invalid_age'
        )
